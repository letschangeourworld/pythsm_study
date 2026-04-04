"""
rtls_algorithms.py — Signal processing & positioning algorithms
===============================================================
RTLS System v2.0.0

포함 알고리즘:
  - HeightCorrector  : 3D→2D 거리 높이 보정
  - DistKF           : 1D 거리 칼만 필터 (스레드 안전)
  - WLS              : Weighted Least Squares 위치 추정
  - AdaptiveEKF      : 적응형 Extended Kalman Filter (IMM-ready)

모든 클래스는 스레드 안전(thread-safe)하게 설계됩니다.
공유 상태는 threading.Lock으로 보호됩니다.
"""

from __future__ import annotations

import logging
import threading
from collections import deque
from typing import Dict, Optional, Tuple

import numpy as np
from scipy.optimize import least_squares

from rtls_config import EKFConfig, RTLSConfig, WLSConfig

log = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# 1. Height Corrector
# ──────────────────────────────────────────────────────────────

class HeightCorrector:
    """
    앵커 설치 높이와 태그 높이 차이를 이용해
    3D 측정 거리를 2D 수평 거리로 보정합니다.

    수식:
        d_2d = sqrt(d_3d² - dz²),  dz = h_anchor - h_tag

    Notes:
        - enabled 속성은 런타임에 토글 가능합니다 (스레드 안전).
        - d_3d < dz 인 물리적으로 불가능한 케이스는 0.10m로 클리핑합니다.
    """

    MIN_DIST_M = 0.10  # 물리적 최솟값

    def __init__(self, cfg: RTLSConfig) -> None:
        self._lock = threading.Lock()
        self._enabled: bool = cfg.positioning.height_correction.enabled
        self._dz: Dict[str, float] = {
            name: anchor.height - cfg.tag_height
            for name, anchor in cfg.anchors.items()
        }
        log.info(
            "[HeightCorrector] enabled=%s  dz=%s",
            self._enabled,
            {k: f"{v:.2f}m" for k, v in self._dz.items()},
        )

    # ── Properties (스레드 안전) ──────────────────────────────

    @property
    def enabled(self) -> bool:
        with self._lock:
            return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        with self._lock:
            self._enabled = value
        log.info("[HeightCorrector] enabled → %s", value)

    def dz(self, anchor: str) -> float:
        """앵커-태그 높이 차이 반환 (m)."""
        return self._dz.get(anchor, 0.0)

    # ── Core ─────────────────────────────────────────────────

    def correct(self, anchor: str, d_raw: float) -> float:
        """
        3D 거리 → 2D 수평 거리 변환.

        Args:
            anchor: 앵커 이름 (예: "A2")
            d_raw:  측정 거리 (m)

        Returns:
            높이 보정된 2D 거리 (m). 보정 비활성화 시 d_raw 반환.
        """
        with self._lock:
            enabled = self._enabled
        if not enabled:
            return d_raw

        dz = self._dz.get(anchor, 0.0)
        if abs(dz) < 1e-6:
            return d_raw

        d_h2 = d_raw ** 2 - dz ** 2
        if d_h2 <= 0.0:
            return self.MIN_DIST_M
        return float(np.sqrt(d_h2))


# ──────────────────────────────────────────────────────────────
# 2. 1D Distance Kalman Filter
# ──────────────────────────────────────────────────────────────

class DistKF:
    """
    앵커별 거리 측정값을 스무딩하는 1D 칼만 필터.

    - 스레드 안전: 모든 공개 메서드는 내부 Lock으로 보호됩니다.
    - 신선도(freshness) 기반 유효성 검사를 제공합니다.

    State:
        x̂ (float): 필터 추정 거리
        P (float): 추정 오차 공분산
    """

    _Q = 0.01   # 프로세스 노이즈 분산
    _R = 0.05   # 측정 노이즈 분산

    def __init__(self, valid_age_sec: float = 0.8, buf_size: int = 8) -> None:
        self._lock = threading.Lock()
        self._valid_age = valid_age_sec
        self._x: float = 0.0
        self._P: float = 1.0
        self._buf: deque[float] = deque(maxlen=buf_size)
        self._diff_buf: deque[float] = deque(maxlen=4)
        self._ts: Optional[float] = None
        self._initialized: bool = False

    def update(self, z: float) -> float:
        """
        새 측정값으로 필터를 업데이트합니다.

        Args:
            z: 측정 거리 (m)

        Returns:
            필터링된 거리 추정값 (m)
        """
        import time as _time

        with self._lock:
            if not self._initialized:
                self._x = z
                self._initialized = True
            else:
                P_pred = self._P + self._Q
                K      = P_pred / (P_pred + self._R)
                innov  = z - self._x
                self._x += K * innov
                self._P  = (1.0 - K) * P_pred

                if self._buf:
                    self._diff_buf.append(abs(z - self._buf[-1]))

            self._buf.append(z)
            self._ts = _time.monotonic()
            return self._x

    def is_fresh(self) -> bool:
        """마지막 업데이트가 valid_age_sec 이내인지 확인합니다."""
        import time as _time

        with self._lock:
            if self._ts is None:
                return False
            return (_time.monotonic() - self._ts) < self._valid_age

    def avg_diff(self) -> float:
        """최근 측정값 변화량 평균 (노이즈 지표)."""
        with self._lock:
            return float(np.mean(self._diff_buf)) if self._diff_buf else 0.0

    def reset(self) -> None:
        """필터 상태를 초기화합니다."""
        with self._lock:
            self._x = 0.0
            self._P = 1.0
            self._buf.clear()
            self._diff_buf.clear()
            self._ts = None
            self._initialized = False


# ──────────────────────────────────────────────────────────────
# 3. WLS Position Estimator
# ──────────────────────────────────────────────────────────────

class WLS:
    """
    Weighted Least Squares 기반 초기 위치 추정기.

    - 각 앵커 거리의 신뢰도(1/d²)를 가중치로 사용합니다.
    - 아웃라이어 감지(중앙값 기반)와 이동 제한(max_jump)을 포함합니다.
    - EKF 초기화 및 폴백(fallback)용으로 사용됩니다.

    스레드 안전: 인스턴스 Lock으로 보호됩니다.
    """

    def __init__(
        self,
        anchor_positions: Dict[str, np.ndarray],
        cfg: WLSConfig,
        max_dist_m: float = 22.0,
        min_anchors: int = 3,
    ) -> None:
        self._lock = threading.Lock()
        self._keys   = list(anchor_positions.keys())
        self._coords = np.array(list(anchor_positions.values()), dtype=float)
        self._cfg    = cfg
        self._max_dist   = max_dist_m
        self._min_anchors= min_anchors

        self._hist: Dict[str, deque] = {
            k: deque(maxlen=10) for k in anchor_positions
        }
        self._prev: Optional[np.ndarray] = None

    def estimate(self, dists: Dict[str, float]) -> Optional[np.ndarray]:
        """
        측정 거리 딕셔너리로부터 2D 위치를 추정합니다.

        Args:
            dists: {앵커명: 거리(m)} 딕셔너리

        Returns:
            추정 위치 [x, y] (m), 앵커 부족 시 None
        """
        with self._lock:
            return self._estimate_inner(dists)

    def _estimate_inner(
        self, dists: Dict[str, float]
    ) -> Optional[np.ndarray]:
        idx, vd, vw = [], [], []

        for i, k in enumerate(self._keys):
            d = dists.get(k)
            if d is None or not (0.0 < d <= self._max_dist):
                continue

            outlier = self._is_outlier(k, d)
            w = 1e-6 if outlier else 1.0 / max(d ** 2, 0.01)
            if not outlier:
                self._hist[k].append(d)

            idx.append(i)
            vd.append(d)
            vw.append(np.sqrt(w))

        if len(idx) < self._min_anchors:
            return None

        anc = self._coords[idx]
        vd  = np.array(vd, dtype=float)
        vw  = np.array(vw, dtype=float)

        # 가중 평균을 초기 추정값으로 사용
        w_sum = vw.sum() or 1.0
        x0    = (vw @ anc) / w_sum

        res = least_squares(
            lambda p: vw * (np.linalg.norm(anc - p, axis=1) - vd),
            x0,
            method="lm",
        )
        pos = res.x

        # 최대 이동 제한
        if self._prev is not None:
            delta = float(np.linalg.norm(pos - self._prev))
            if delta > self._cfg.max_jump_m:
                pos = (
                    self._prev
                    + (pos - self._prev) / delta * self._cfg.max_jump_m
                )

        self._prev = pos.copy()
        return pos

    def _is_outlier(self, anchor: str, d: float) -> bool:
        h = self._hist[anchor]
        return (
            len(h) >= 4
            and abs(d - float(np.median(h))) > self._cfg.outlier_threshold_m
        )

    def reset(self) -> None:
        with self._lock:
            for h in self._hist.values():
                h.clear()
            self._prev = None


# ──────────────────────────────────────────────────────────────
# 4. Adaptive Extended Kalman Filter
# ──────────────────────────────────────────────────────────────

class AdaptiveEKF:
    """
    적응형 Extended Kalman Filter (위치+속도 상태 추정).

    상태 벡터: x = [x, y, vx, vy]ᵀ

    개선 사항 vs. 기존 EKF:
    - 적응형 측정 노이즈 R (Innovation Covariance Matching):
        잔차 통계를 실시간 추적하여 R을 동적으로 업데이트합니다.
        센서 품질 저하나 멀티패스 환경에서 견고성이 향상됩니다.
    - Mahalanobis 거리 기반 아웃라이어 게이팅:
        통계적으로 비정상적인 측정값을 EKF 업데이트에서 제외합니다.
    - 공분산 대칭화 (Joseph form):
        수치 안정성을 위해 P = (I-KH)P(I-KH)ᵀ + KRKᵀ를 사용합니다.
    - 속도 클리핑으로 물리적 제약 적용

    스레드 안전: 모든 공개 메서드는 내부 Lock으로 보호됩니다.
    """

    # Mahalanobis 게이팅 임계값 (chi-squared, DOF=1, 99.9%)
    _GATE_THRESHOLD = 10.83

    def __init__(
        self,
        anchor_positions: Dict[str, np.ndarray],
        cfg: EKFConfig,
    ) -> None:
        self._lock      = threading.Lock()
        self._anchors   = anchor_positions
        self._cfg       = cfg

        # 상태
        self._x    = np.zeros((4, 1), dtype=float)
        self._P    = np.eye(4, dtype=float) * cfg.init_covariance
        self._Q    = cfg.Q
        self._R    = cfg.measurement_noise

        # 적응형 R 추정
        self._innov_buf: deque[float] = deque(maxlen=cfg.adaptive_r_window)
        self._S_buf:     deque[float] = deque(maxlen=cfg.adaptive_r_window)

        # 이력
        self._pos_hist: deque[np.ndarray] = deque(maxlen=8)
        self._initialized = False

        log.debug(
            "[AdaptiveEKF] Q_diag=%s  R=%.4f  adaptive=%s",
            np.diag(self._Q).tolist(),
            self._R,
            cfg.adaptive_r,
        )

    # ── Public API ───────────────────────────────────────────

    @property
    def initialized(self) -> bool:
        with self._lock:
            return self._initialized

    def init(self, pos: np.ndarray) -> None:
        """WLS 추정값으로 EKF를 초기화합니다."""
        with self._lock:
            self._x[:] = 0.0
            self._x[0, 0] = float(pos[0])
            self._x[1, 0] = float(pos[1])
            self._P    = np.eye(4) * self._cfg.init_covariance
            self._pos_hist.clear()
            self._innov_buf.clear()
            self._S_buf.clear()
            self._initialized = True
        log.info("[AdaptiveEKF] Initialized at (%.3f, %.3f)", pos[0], pos[1])

    def predict(self, dt: Optional[float] = None) -> None:
        """
        운동 모델로 상태를 예측합니다 (등속도 모델).

        Args:
            dt: 시간 간격 (None이면 cfg.dt 사용)
        """
        with self._lock:
            if not self._initialized:
                return
            _dt = dt if dt is not None else self._cfg.dt
            F = self._state_transition(_dt)
            self._x = F @ self._x
            self._P = F @ self._P @ F.T + self._Q

    def update(
        self,
        distances: Dict[str, float],
        max_dist: float = 22.0,
    ) -> None:
        """
        앵커별 거리 측정값으로 상태를 업데이트합니다.

        Args:
            distances: {앵커명: 거리(m)} 딕셔너리
            max_dist:  유효 거리 상한 (m)
        """
        with self._lock:
            if not self._initialized:
                return

            for ak, av in self._anchors.items():
                z = distances.get(ak)
                if z is None or not (0.0 < z <= max_dist):
                    continue

                # 예측 거리
                px, py = self._x[0, 0], self._x[1, 0]
                dx, dy = px - av[0], py - av[1]
                pred   = np.sqrt(dx * dx + dy * dy) + 1e-9

                # Jacobian H
                H = np.array([[dx / pred, dy / pred, 0.0, 0.0]])

                # Innovation
                innov = z - pred
                S     = float(H @ self._P @ H.T) + self._R

                # Mahalanobis 게이팅
                mahal = innov ** 2 / S
                if mahal > self._GATE_THRESHOLD:
                    log.debug(
                        "[AdaptiveEKF] Gated %s: innov=%.3f mahal=%.2f",
                        ak, innov, mahal,
                    )
                    continue

                # 적응형 R 업데이트
                if self._cfg.adaptive_r:
                    self._innov_buf.append(innov ** 2)
                    self._S_buf.append(S)
                    if len(self._innov_buf) >= 3:
                        # Innovation covariance matching
                        eps_hat = float(np.mean(self._innov_buf))
                        S_hat   = float(np.mean(self._S_buf))
                        # R̂ = ε̂ - (S - R)  →  R 추정
                        r_est   = max(eps_hat - (S_hat - self._R), 1e-4)
                        # 지수이동평균으로 부드럽게 추적
                        self._R = 0.95 * self._R + 0.05 * r_est

                # Kalman gain
                K = (self._P @ H.T) / S

                # 상태 업데이트 (Joseph form으로 공분산 업데이트)
                self._x = self._x + K * innov
                I_KH    = np.eye(4) - K @ H
                # Joseph form: P = (I-KH)P(I-KH)ᵀ + KRKᵀ
                self._P = (
                    I_KH @ self._P @ I_KH.T
                    + K * self._R * K.T
                )

            # 속도 클리핑
            spd = np.linalg.norm(self._x[2:, 0])
            if spd > self._cfg.max_speed_m_s:
                self._x[2:, 0] *= self._cfg.max_speed_m_s / spd

            self._pos_hist.append(self._get_pos())

    def get_pos(self) -> np.ndarray:
        """현재 위치 추정값 [x, y] (m) 반환."""
        with self._lock:
            return self._get_pos()

    def get_vel(self) -> np.ndarray:
        """현재 속도 추정값 [vx, vy] (m/s) 반환."""
        with self._lock:
            return self._x[2:4, 0].copy()

    def pos_std(self) -> float:
        """최근 위치 히스토리의 표준편차 (안정성 지표)."""
        with self._lock:
            if len(self._pos_hist) < 3:
                return 99.0
            pts = np.array(self._pos_hist)
            return float(np.max(np.std(pts, axis=0)))

    def speed(self) -> float:
        """현재 속력 (m/s)."""
        with self._lock:
            return float(np.linalg.norm(self._x[2:4, 0]))

    def current_R(self) -> float:
        """현재 적응형 R 값 반환 (진단용)."""
        with self._lock:
            return self._R

    def reset(self) -> None:
        """EKF 상태를 초기화합니다."""
        with self._lock:
            self._x[:] = 0.0
            self._P    = np.eye(4) * self._cfg.init_covariance
            self._R    = self._cfg.measurement_noise
            self._pos_hist.clear()
            self._innov_buf.clear()
            self._S_buf.clear()
            self._initialized = False

    # ── Internal helpers ─────────────────────────────────────

    def _get_pos(self) -> np.ndarray:
        """Lock 없이 위치 반환 (내부 전용)."""
        return self._x[0:2, 0].copy()

    @staticmethod
    def _state_transition(dt: float) -> np.ndarray:
        """등속도 운동 상태 전이 행렬 F."""
        return np.array(
            [
                [1.0, 0.0,  dt, 0.0],
                [0.0, 1.0, 0.0,  dt],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=float,
        )
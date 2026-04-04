"""
rtls_core.py — Thread-safe data pipeline & tag tracking
========================================================
RTLS System v2.0.0

포함 모듈:
  - AnchorGrouper   : 타임윈도우 기반 앵커 데이터 그룹핑 (스레드 안전)
  - ConnManager     : 태그 연결 상태 관리 (스레드 안전)
  - TagTracker      : 태그별 위치 추정 파이프라인
  - SerialReceiver  : USB 시리얼 데이터 수신기
  - TCPReceiver     : TCP 소켓 데이터 수신기
  - parse_line      : 앵커 데이터 라인 파서

스레드 안전 설계 원칙:
  - 모든 공유 상태는 threading.Lock 또는 threading.RLock으로 보호
  - 큐(Queue)를 통해 스레드 간 데이터 전달
  - 외부에서 접근 가능한 모든 속성은 락 내부에서만 변경
"""

from __future__ import annotations

import logging
import queue
import re
import socket
import threading
import time
from collections import defaultdict, deque
from enum import Enum, auto
from typing import Dict, Optional, Tuple

import numpy as np

from rtls_algorithms import AdaptiveEKF, DistKF, HeightCorrector, WLS
from rtls_config import RTLSConfig, SerialConnection, TCPConnection

log = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
# 파서
# ──────────────────────────────────────────────────────────────

_LINE_RE = re.compile(
    r"TAG[:\s]*([0-9A-Fa-f]+)"
    r".*?DIST[:\s]*(\d+)"
    r".*?ANCHOR[:\s]*([0-9A-Fa-f]+)",
    re.IGNORECASE,
)


def parse_line(
    line: str,
    anchor_name: str,
    cfg: RTLSConfig,
) -> Optional[Tuple[str, float]]:
    """
    앵커 펌웨어 출력 라인을 파싱합니다.

    Expected format:
        "TAG:0064 DIST:900 ANCHOR:0002"

    Args:
        line:        수신된 원시 문자열
        anchor_name: 이 수신기가 담당하는 앵커 이름 (예: "A2")
        cfg:         RTLSConfig 인스턴스

    Returns:
        (tag_name, dist_m) 튜플, 파싱 실패 또는 다른 앵커 데이터면 None
    """
    m = _LINE_RE.search(line)
    if not m:
        return None

    tag_hex    = m.group(1).lower().zfill(4)
    dist_raw   = int(m.group(2))
    anchor_hex = m.group(3).lower().zfill(4)

    # 앵커 검증: 이 수신기 담당 앵커가 맞는지 확인
    anchor_from_hw = cfg.anchor_hw_map.get(anchor_hex)
    if anchor_from_hw is not None and anchor_from_hw != anchor_name:
        return None

    # 태그명 매핑
    tag_name = cfg.tag_hw_map.get(tag_hex, f"TAG_{tag_hex}")

    # 거리 변환 (mm → m)
    dist_m = dist_raw / 1000.0 if dist_raw > 100 else float(dist_raw)

    pos_cfg = cfg.positioning
    if not (0.0 < dist_m <= pos_cfg.max_dist_m):
        return None

    return tag_name, dist_m


# ──────────────────────────────────────────────────────────────
# 연결 상태
# ──────────────────────────────────────────────────────────────

class TagStatus(Enum):
    WAITING   = auto()
    CONNECTED = auto()
    TIMEOUT   = auto()


class ConnManager:
    """
    태그 연결 상태를 추적합니다.

    스레드 안전: 모든 메서드는 내부 Lock으로 보호됩니다.
    """

    def __init__(self, tag_ids: list[str], timeout_sec: float) -> None:
        self._lock       = threading.Lock()
        self._tag_ids    = tag_ids
        self._timeout    = timeout_sec
        self._last_rx:   Dict[str, Optional[float]] = {t: None for t in tag_ids}
        self._status:    Dict[str, TagStatus]        = {
            t: TagStatus.WAITING for t in tag_ids
        }

    def mark(self, tid: str) -> None:
        """태그 데이터 수신 기록."""
        with self._lock:
            self._last_rx[tid] = time.monotonic()
            if self._status[tid] != TagStatus.CONNECTED:
                log.info("[ConnManager] %s → CONNECTED", tid)
                self._status[tid] = TagStatus.CONNECTED

    def tick(self) -> Tuple[set, set]:
        """
        타임아웃 체크를 수행합니다.

        Returns:
            (newly_disconnected, newly_reconnected) 태그 집합
        """
        now  = time.monotonic()
        disc = set()
        recon= set()

        with self._lock:
            prev_active = {t for t, s in self._status.items()
                           if s == TagStatus.CONNECTED}

            for t in self._tag_ids:
                last = self._last_rx[t]
                if (last is not None
                        and (now - last) > self._timeout
                        and self._status[t] == TagStatus.CONNECTED):
                    self._status[t] = TagStatus.TIMEOUT
                    log.warning("[ConnManager] %s → TIMEOUT", t)

            curr_active = {t for t, s in self._status.items()
                           if s == TagStatus.CONNECTED}

        disc  = prev_active - curr_active
        recon = curr_active - prev_active
        return disc, recon

    def status(self, tid: str) -> TagStatus:
        with self._lock:
            return self._status[tid]

    def is_active(self, tid: str) -> bool:
        return self.status(tid) == TagStatus.CONNECTED

    def elapsed(self, tid: str) -> float:
        """마지막 수신 이후 경과 시간 (s). 미수신 시 -1."""
        with self._lock:
            last = self._last_rx[tid]
            return -1.0 if last is None else time.monotonic() - last

    @property
    def active_list(self) -> list[str]:
        with self._lock:
            return [t for t in self._tag_ids
                    if self._status[t] == TagStatus.CONNECTED]

    @property
    def summary(self) -> str:
        parts = []
        with self._lock:
            for t in self._tag_ids:
                st = self._status[t]
                el = self.elapsed(t)
                if st == TagStatus.WAITING:
                    parts.append(f"{t}:WAIT")
                elif st == TagStatus.CONNECTED:
                    parts.append(f"{t}:OK({el:.1f}s)")
                else:
                    parts.append(f"{t}:TO({el:.0f}s)")
        return " | ".join(parts)


# ──────────────────────────────────────────────────────────────
# 앵커 데이터 그룹핑
# ──────────────────────────────────────────────────────────────

class AnchorGrouper:
    """
    앵커별로 도착하는 거리 데이터를 태그 기준으로 타임윈도우 내에 묶습니다.

    완성된 그룹은 completed 큐에 넣습니다.
    소비자(TagTracker)는 큐에서 꺼내 처리합니다.

    스레드 안전: 내부 버퍼 접근은 Lock으로 보호됩니다.
    """

    def __init__(
        self,
        window_sec: float,
        min_anchors: int,
    ) -> None:
        self._window     = window_sec
        self._min_anchors= min_anchors
        self._lock       = threading.Lock()
        self._buf:       Dict[str, Dict[str, Tuple[float, float]]] = defaultdict(dict)
        self.completed:  queue.Queue = queue.Queue()
        self._total      = 0

    def push(
        self,
        anchor: str,
        tag: str,
        dist_m: float,
        ts: float,
    ) -> None:
        """
        앵커 거리 데이터를 버퍼에 추가하고 그룹 완성 여부를 확인합니다.

        Args:
            anchor: 앵커 이름
            tag:    태그 이름
            dist_m: 거리 (m)
            ts:     수신 타임스탬프 (monotonic)
        """
        with self._lock:
            self._buf[tag][anchor] = (dist_m, ts)
            self._try_flush(tag, ts)

    def _try_flush(self, tag: str, now: float) -> None:
        """윈도우 내 데이터가 충분하면 그룹을 완성합니다."""
        data = self._buf[tag]

        # 오래된 항목 제거
        fresh = {
            ak: (d, t)
            for ak, (d, t) in data.items()
            if now - t < self._window
        }
        self._buf[tag] = fresh

        if len(fresh) < self._min_anchors:
            return

        dists = {ak: d for ak, (d, _) in fresh.items()}
        self._total += 1
        group_id = self._total
        self.completed.put_nowait({
            "tag":   tag,
            "dists": dists,
            "ts":    now,
            "id":    group_id,
        })
        self._buf[tag] = {}

        log.debug(
            "[Grouper #%d] %s: %s",
            group_id, tag,
            {ak: f"{d*1000:.0f}mm" for ak, d in dists.items()},
        )

    def flush_stale(self) -> None:
        """오래된 버퍼 항목을 주기적으로 정리합니다."""
        cutoff = time.monotonic() - self._window * 3
        with self._lock:
            for tag in list(self._buf):
                self._buf[tag] = {
                    ak: (d, t)
                    for ak, (d, t) in self._buf[tag].items()
                    if t > cutoff
                }

    @property
    def total_groups(self) -> int:
        return self._total


# ──────────────────────────────────────────────────────────────
# 태그 추적기
# ──────────────────────────────────────────────────────────────

class TagTracker:
    """
    단일 태그의 위치 추정 파이프라인.

    파이프라인:
        raw dist → DistKF → HeightCorrector → WLS → AdaptiveEKF → LERP

    dist_filt, fused_pos, smooth_pos 등의 출력 속성은
    get_*() 메서드를 통해 스레드 안전하게 접근합니다.
    """

    def __init__(
        self,
        tid: str,
        cfg: RTLSConfig,
        anchor_positions: Dict[str, np.ndarray],
        hcorr: HeightCorrector,
        room_bounds: Tuple[np.ndarray, np.ndarray],
    ) -> None:
        self.tid   = tid
        self._cfg  = cfg
        self._hcorr= hcorr
        self._min_pos, self._max_pos = room_bounds

        pos_cfg = cfg.positioning

        self._ekf = AdaptiveEKF(anchor_positions, pos_cfg.ekf)
        self._wls = WLS(
            anchor_positions,
            pos_cfg.wls,
            pos_cfg.max_dist_m,
            pos_cfg.min_anchors,
        )
        self._dist_kf: Dict[str, DistKF] = {
            ak: DistKF(pos_cfg.dist_valid_age_sec, pos_cfg.wls.dist_buffer_size)
            for ak in anchor_positions
        }

        # 출력 상태 (Lock으로 보호)
        self._lock        = threading.Lock()
        self._dist_filt:  Dict[str, float] = {}
        self._fused_pos:  Optional[np.ndarray] = None
        self._smooth_pos: Optional[np.ndarray] = None
        self._wls_pos:    Optional[np.ndarray] = None
        self._residuals:  Dict[str, Tuple[float, float, float]] = {}
        self._err_count   = 0
        self._frame_cnt   = 0

    # ── Pipeline ─────────────────────────────────────────────

    def push_distance(self, anchor: str, d_raw: float) -> None:
        """원시 거리 데이터를 DistKF로 필터링해 버퍼에 저장합니다."""
        try:
            d_h = self._hcorr.correct(anchor, d_raw)
            max_d = self._cfg.positioning.max_dist_m
            if not (0.0 < d_h <= max_d):
                return
            d_f = self._dist_kf[anchor].update(d_h)
            if 0.0 < d_f <= max_d:
                with self._lock:
                    self._dist_filt[anchor] = d_f
        except Exception:
            with self._lock:
                self._err_count += 1
            log.exception("[%s] push_distance error", self.tid)

    def compute(self) -> None:
        """WLS + EKF 위치 추정을 실행합니다."""
        try:
            self._compute_inner()
        except Exception:
            with self._lock:
                self._err_count += 1
            log.exception("[%s] compute error", self.tid)

    def _compute_inner(self) -> None:
        with self._lock:
            valid = {
                k: v
                for k, v in self._dist_filt.items()
                if v is not None
                and v > 0.0
                and self._dist_kf[k].is_fresh()
            }

        if len(valid) < self._cfg.positioning.min_anchors:
            return

        wls_pos = self._wls.estimate(valid)
        if wls_pos is None:
            return

        wls_pos = np.clip(wls_pos, self._min_pos, self._max_pos)

        with self._lock:
            self._wls_pos = wls_pos.copy()

        if not self._ekf.initialized:
            self._ekf.init(wls_pos)
            with self._lock:
                self._fused_pos = wls_pos.copy()
                self._frame_cnt = 0
            return

        with self._lock:
            self._frame_cnt += 1

        self._ekf.predict()
        self._ekf.update(valid, self._cfg.positioning.max_dist_m)

        ekf_pos = np.clip(
            self._ekf.get_pos(), self._min_pos, self._max_pos
        )

        # 잔차 계산
        residuals: Dict[str, Tuple[float, float, float]] = {}
        anchor_positions = self._cfg.anchor_positions()
        for ak, av in anchor_positions.items():
            if ak not in valid:
                continue
            pred = float(np.linalg.norm(ekf_pos - av))
            meas = valid[ak]
            residuals[ak] = (meas, pred, meas - pred)

        with self._lock:
            self._fused_pos  = ekf_pos
            self._residuals  = residuals

    def lerp(self, alpha: float = 0.35) -> None:
        """EKF 출력을 선형 보간으로 스무딩합니다."""
        with self._lock:
            fp = self._fused_pos
            if fp is None:
                return
            if self._smooth_pos is None:
                self._smooth_pos = fp.copy()
                return
            delta = fp - self._smooth_pos
            dist  = float(np.linalg.norm(delta))
            if dist < 0.04:
                self._smooth_pos = fp.copy()
            else:
                self._smooth_pos = self._smooth_pos + alpha * delta

    # ── Accessors (스레드 안전) ───────────────────────────────

    def get_fused_pos(self) -> Optional[np.ndarray]:
        with self._lock:
            return self._fused_pos.copy() if self._fused_pos is not None else None

    def get_smooth_pos(self) -> Optional[np.ndarray]:
        with self._lock:
            return self._smooth_pos.copy() if self._smooth_pos is not None else None

    def get_wls_pos(self) -> Optional[np.ndarray]:
        with self._lock:
            return self._wls_pos.copy() if self._wls_pos is not None else None

    def get_dist_filt(self) -> Dict[str, float]:
        with self._lock:
            return dict(self._dist_filt)

    def get_residuals(self) -> Dict[str, Tuple[float, float, float]]:
        with self._lock:
            return dict(self._residuals)

    def get_err_count(self) -> int:
        with self._lock:
            return self._err_count

    def speed(self) -> float:
        return self._ekf.speed()

    def pos_std(self) -> float:
        return self._ekf.pos_std()

    def is_dist_fresh(self, anchor: str) -> bool:
        return self._dist_kf[anchor].is_fresh()

    def reset(self) -> None:
        """추적기 상태를 초기화합니다."""
        self._ekf.reset()
        self._wls.reset()
        for dk in self._dist_kf.values():
            dk.reset()
        with self._lock:
            self._dist_filt  = {}
            self._fused_pos  = None
            self._smooth_pos = None
            self._wls_pos    = None
            self._residuals  = {}
            self._err_count  = 0
            self._frame_cnt  = 0
        log.info("[%s] TagTracker reset", self.tid)


# ──────────────────────────────────────────────────────────────
# 수신기 베이스
# ──────────────────────────────────────────────────────────────

class _BaseReceiver:
    """수신기 공통 인터페이스."""

    def __init__(
        self,
        anchor_name: str,
        grouper: AnchorGrouper,
        conn_mgr: ConnManager,
        hcorr: HeightCorrector,
        cfg: RTLSConfig,
    ) -> None:
        self.anchor_name  = anchor_name
        self._grouper     = grouper
        self._conn_mgr    = conn_mgr
        self._hcorr       = hcorr
        self._cfg         = cfg
        self._running     = False
        self._rx_count    = 0
        self._err_count   = 0
        self._connected   = False
        self._lock        = threading.Lock()

    @property
    def connected(self) -> bool:
        with self._lock:
            return self._connected

    @property
    def rx_count(self) -> int:
        return self._rx_count

    def _handle_line(self, line: str) -> None:
        """파싱 및 그룹화 공통 처리."""
        result = parse_line(line, self.anchor_name, self._cfg)
        if result is None:
            return
        tag_name, dist_m = result
        ts = time.monotonic()
        d_h = self._hcorr.correct(self.anchor_name, dist_m)
        self._grouper.push(self.anchor_name, tag_name, d_h, ts)
        self._conn_mgr.mark(tag_name)
        self._rx_count += 1

    def start(self) -> None:
        self._running = True
        t = threading.Thread(target=self._run, daemon=True, name=f"rx-{self.anchor_name}")
        t.start()

    def stop(self) -> None:
        self._running = False

    def _run(self) -> None:
        raise NotImplementedError


# ──────────────────────────────────────────────────────────────
# 시리얼 수신기
# ──────────────────────────────────────────────────────────────

class SerialReceiver(_BaseReceiver):
    """
    USB 시리얼로 직접 연결된 앵커에서 데이터를 수신합니다.
    연결 끊김 시 RECONNECT_SEC 후 자동 재연결합니다.
    """

    def __init__(
        self,
        anchor_name: str,
        conn_cfg: SerialConnection,
        grouper: AnchorGrouper,
        conn_mgr: ConnManager,
        hcorr: HeightCorrector,
        cfg: RTLSConfig,
    ) -> None:
        super().__init__(anchor_name, grouper, conn_mgr, hcorr, cfg)
        self._port = conn_cfg.port
        self._baud = conn_cfg.baud
        self._reconnect_sec = cfg.connection.reconnect_sec

    def _run(self) -> None:
        try:
            import serial
        except ImportError:
            log.error("[%s] pyserial not installed: pip install pyserial", self.anchor_name)
            return

        log.info("[%s] SerialReceiver starting on %s @ %d", self.anchor_name, self._port, self._baud)

        while self._running:
            ser = None
            try:
                ser = serial.Serial(self._port, self._baud, timeout=1)
                with self._lock:
                    self._connected = True
                log.info("[%s] Serial connected: %s", self.anchor_name, self._port)
                self._err_count = 0

                while self._running:
                    if ser.in_waiting:
                        try:
                            raw  = ser.readline()
                            line = raw.decode("utf-8", errors="ignore").strip()
                            if line:
                                self._handle_line(line)
                        except Exception:
                            self._err_count += 1
                            if self._err_count % 100 == 1:
                                log.exception("[%s] read error", self.anchor_name)
                    time.sleep(0.001)

            except Exception as exc:
                with self._lock:
                    self._connected = False
                log.warning("[%s] Serial error: %s — retry in %.1fs",
                            self.anchor_name, exc, self._reconnect_sec)
                if self._running:
                    time.sleep(self._reconnect_sec)
            finally:
                if ser:
                    try: ser.close()
                    except Exception: pass


# ──────────────────────────────────────────────────────────────
# TCP 수신기
# ──────────────────────────────────────────────────────────────

class TCPReceiver(_BaseReceiver):
    """
    원격 Pi의 rtls_agent.py에 TCP로 접속하여 데이터를 수신합니다.
    연결 실패/끊김 시 자동 재접속합니다.
    """

    def __init__(
        self,
        anchor_name: str,
        conn_cfg: TCPConnection,
        grouper: AnchorGrouper,
        conn_mgr: ConnManager,
        hcorr: HeightCorrector,
        cfg: RTLSConfig,
    ) -> None:
        super().__init__(anchor_name, grouper, conn_mgr, hcorr, cfg)
        self._host          = conn_cfg.host
        self._port          = conn_cfg.port
        self._tcp_timeout   = cfg.connection.tcp_timeout_sec
        self._reconnect_sec = cfg.connection.reconnect_sec

    def _run(self) -> None:
        log.info("[%s] TCPReceiver starting → %s:%d",
                 self.anchor_name, self._host, self._port)

        while self._running:
            sock = None
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                sock.settimeout(self._tcp_timeout)
                sock.connect((self._host, self._port))
                sock.settimeout(2.0)

                with self._lock:
                    self._connected = True
                log.info("[%s] TCP connected: %s:%d",
                         self.anchor_name, self._host, self._port)
                self._err_count = 0

                buf = ""
                while self._running:
                    try:
                        chunk = sock.recv(4096)
                        if not chunk:
                            log.warning("[%s] TCP connection closed", self.anchor_name)
                            break
                        buf += chunk.decode("utf-8", errors="ignore")
                        while "\n" in buf:
                            line, buf = buf.split("\n", 1)
                            line = line.strip()
                            if line:
                                self._handle_line(line)
                    except socket.timeout:
                        continue
                    except Exception:
                        log.exception("[%s] TCP recv error", self.anchor_name)
                        break

            except (ConnectionRefusedError, socket.timeout, OSError) as exc:
                log.warning("[%s] TCP connect failed: %s — retry in %.1fs",
                            self.anchor_name, exc, self._reconnect_sec)
            except Exception:
                log.exception("[%s] TCP error", self.anchor_name)
            finally:
                with self._lock:
                    self._connected = False
                if sock:
                    try: sock.close()
                    except Exception: pass

            if self._running:
                time.sleep(self._reconnect_sec)
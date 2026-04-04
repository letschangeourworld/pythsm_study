"""
tests/test_rtls.py — Unit tests for RTLS System v2.0.0
=======================================================

실행:
    pytest tests/test_rtls.py -v
    pytest tests/test_rtls.py -v --tb=short
"""

from __future__ import annotations

import threading
import time
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import yaml

# ──────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────

SAMPLE_CONFIG_YAML = textwrap.dedent("""
system:
  version: "2.0.0"
  simulation_mode: false
  log_dir: "/tmp/rtls_test_logs"
  log_level: "WARNING"

anchors:
  A2:
    x: 0.0
    y: 12.5
    height: 2.5
    connection:
      type: serial
      port: /dev/ttyACM0
      baud: 115200
  A3:
    x: 15.0
    y: 0.0
    height: 3.5
    connection:
      type: tcp
      host: "192.168.1.103"
      port: 9003
  A4:
    x: 15.0
    y: 12.5
    height: 2.5
    connection:
      type: tcp
      host: "192.168.1.104"
      port: 9004

hardware_map:
  anchors:
    "0002": A2
    "0003": A3
    "0004": A4
  tags:
    "0064": TAG1
    "0065": TAG2

tags:
  height: 1.0

positioning:
  min_anchors: 3
  group_window_sec: 0.15
  max_dist_m: 22.0
  dist_valid_age_sec: 0.8
  height_correction:
    enabled: true
  wls:
    max_jump_m: 4.0
    outlier_threshold_m: 1.5
    dist_buffer_size: 8
  ekf:
    process_noise: [0.05, 0.05, 0.20, 0.20]
    measurement_noise: 0.25
    init_covariance: 2.0
    dt: 0.1
    adaptive_r: true
    adaptive_r_window: 10
    max_speed_m_s: 5.0

connection:
  tag_timeout_sec: 5.0
  reconnect_sec: 5.0
  tcp_timeout_sec: 3.0

visualization:
  update_interval_ms: 100
  anchor_colors:
    A2: "#1E8B3E"
    A3: "#D98000"
    A4: "#6B3FA0"
  tag_colors:
    TAG1: "#1565C0"
    TAG2: "#C62828"

simulator:
  move_duration_sec: 8.0
  stop_duration_sec: 5.0
  noise_moving_m: 0.08
  noise_stopped_m: 0.03
""")


@pytest.fixture
def cfg_path(tmp_path: Path) -> Path:
    p = tmp_path / "config.yaml"
    p.write_text(SAMPLE_CONFIG_YAML, encoding="utf-8")
    return p


@pytest.fixture
def cfg(cfg_path: Path):
    from rtls_config import RTLSConfig
    return RTLSConfig.from_yaml(cfg_path)


@pytest.fixture
def anchor_positions(cfg):
    return cfg.anchor_positions()


# ──────────────────────────────────────────────────────────────
# RTLSConfig tests
# ──────────────────────────────────────────────────────────────

class TestRTLSConfig:
    def test_load_yaml(self, cfg):
        assert cfg.version == "2.0.0"
        assert cfg.simulation_mode is False
        assert len(cfg.anchors) == 3

    def test_anchor_positions(self, cfg):
        pos = cfg.anchor_position("A2")
        np.testing.assert_array_almost_equal(pos, [0.0, 12.5])

    def test_anchor_height(self, cfg):
        assert cfg.anchor_height("A3") == pytest.approx(3.5)

    def test_tag_ids(self, cfg):
        ids = cfg.tag_ids()
        assert "TAG1" in ids
        assert "TAG2" in ids

    def test_serial_connection(self, cfg):
        from rtls_config import SerialConnection
        conn = cfg.anchors["A2"].connection
        assert isinstance(conn, SerialConnection)
        assert conn.port == "/dev/ttyACM0"

    def test_tcp_connection(self, cfg):
        from rtls_config import TCPConnection
        conn = cfg.anchors["A3"].connection
        assert isinstance(conn, TCPConnection)
        assert conn.host == "192.168.1.103"
        assert conn.port == 9003

    def test_ekf_Q_matrix(self, cfg):
        Q = cfg.positioning.ekf.Q
        assert Q.shape == (4, 4)
        assert Q[0, 0] == pytest.approx(0.05)
        assert Q[2, 2] == pytest.approx(0.20)

    def test_missing_file_raises(self, tmp_path: Path):
        from rtls_config import RTLSConfig
        with pytest.raises(FileNotFoundError):
            RTLSConfig.from_yaml(tmp_path / "nonexistent.yaml")

    def test_validation_no_anchors(self, tmp_path: Path):
        from rtls_config import RTLSConfig
        bad = yaml.safe_load(SAMPLE_CONFIG_YAML)
        bad["anchors"] = {}
        p = tmp_path / "bad.yaml"
        p.write_text(yaml.dump(bad))
        with pytest.raises(ValueError, match="No anchors"):
            RTLSConfig.from_yaml(p)

    def test_invalid_tcp_port_raises(self, tmp_path: Path):
        from rtls_config import RTLSConfig
        bad = yaml.safe_load(SAMPLE_CONFIG_YAML)
        bad["anchors"]["A3"]["connection"]["port"] = 99999
        p = tmp_path / "bad2.yaml"
        p.write_text(yaml.dump(bad))
        with pytest.raises(ValueError, match="TCP port"):
            RTLSConfig.from_yaml(p)


# ──────────────────────────────────────────────────────────────
# HeightCorrector tests
# ──────────────────────────────────────────────────────────────

class TestHeightCorrector:
    def test_correct_reduces_distance(self, cfg):
        from rtls_algorithms import HeightCorrector
        hc = HeightCorrector(cfg)
        # A2: height=2.5, tag_height=1.0 → dz=1.5
        d_raw = 5.0
        d_corr = hc.correct("A2", d_raw)
        expected = np.sqrt(d_raw ** 2 - 1.5 ** 2)
        assert d_corr == pytest.approx(expected, rel=1e-5)

    def test_correct_disabled(self, cfg):
        from rtls_algorithms import HeightCorrector
        hc = HeightCorrector(cfg)
        hc.enabled = False
        d_raw = 5.0
        assert hc.correct("A2", d_raw) == pytest.approx(d_raw)

    def test_toggle_thread_safety(self, cfg):
        """다중 스레드에서 enabled 토글이 안전한지 확인."""
        from rtls_algorithms import HeightCorrector
        hc = HeightCorrector(cfg)
        errors = []

        def toggle():
            for _ in range(500):
                hc.enabled = not hc.enabled

        def read():
            for _ in range(500):
                try:
                    hc.correct("A2", 5.0)
                except Exception as e:
                    errors.append(e)

        threads = [threading.Thread(target=toggle),
                   threading.Thread(target=read),
                   threading.Thread(target=read)]
        for t in threads: t.start()
        for t in threads: t.join()
        assert not errors, f"Thread safety violation: {errors}"

    def test_physical_limit_clipped(self, cfg):
        from rtls_algorithms import HeightCorrector
        hc = HeightCorrector(cfg)
        # dz=1.5, d_raw=1.0 → d_h² < 0 → MIN_DIST
        d = hc.correct("A2", 1.0)
        assert d == pytest.approx(HeightCorrector.MIN_DIST_M)

    def test_no_dz_anchor(self, cfg):
        """dz ≈ 0인 앵커는 보정 없이 통과."""
        from rtls_algorithms import HeightCorrector, DistKF
        hc = HeightCorrector(cfg)
        # 임의로 dz=0인 앵커 추가
        hc._dz["A_FLAT"] = 0.0
        d_raw = 7.0
        assert hc.correct("A_FLAT", d_raw) == pytest.approx(d_raw)


# ──────────────────────────────────────────────────────────────
# DistKF tests
# ──────────────────────────────────────────────────────────────

class TestDistKF:
    def test_first_update_returns_z(self):
        from rtls_algorithms import DistKF
        kf = DistKF()
        result = kf.update(5.0)
        assert result == pytest.approx(5.0)

    def test_smoothing(self):
        from rtls_algorithms import DistKF
        kf = DistKF()
        vals = [5.0, 5.1, 4.9, 5.05, 5.0]
        results = [kf.update(v) for v in vals]
        # 필터 출력이 입력보다 분산이 작아야 함
        assert np.std(results) < np.std(vals)

    def test_freshness(self):
        from rtls_algorithms import DistKF
        kf = DistKF(valid_age_sec=0.1)
        kf.update(5.0)
        assert kf.is_fresh()
        time.sleep(0.15)
        assert not kf.is_fresh()

    def test_reset(self):
        from rtls_algorithms import DistKF
        kf = DistKF()
        kf.update(5.0)
        kf.reset()
        assert not kf.is_fresh()

    def test_thread_safety(self):
        from rtls_algorithms import DistKF
        kf = DistKF()
        results = []
        errors  = []

        def writer():
            for i in range(200):
                try:
                    kf.update(float(i % 10))
                except Exception as e:
                    errors.append(e)

        def reader():
            for _ in range(200):
                try:
                    kf.is_fresh()
                except Exception as e:
                    errors.append(e)

        threads = [threading.Thread(target=writer),
                   threading.Thread(target=reader),
                   threading.Thread(target=reader)]
        for t in threads: t.start()
        for t in threads: t.join()
        assert not errors


# ──────────────────────────────────────────────────────────────
# WLS tests
# ──────────────────────────────────────────────────────────────

class TestWLS:
    def test_estimate_known_position(self, cfg, anchor_positions):
        """알려진 위치에서 거리를 계산해 WLS로 복원하는지 확인."""
        from rtls_algorithms import WLS
        wls = WLS(anchor_positions, cfg.positioning.wls)

        true_pos = np.array([7.5, 6.25])
        dists = {
            ak: float(np.linalg.norm(true_pos - av))
            for ak, av in anchor_positions.items()
        }

        est = wls.estimate(dists)
        assert est is not None
        np.testing.assert_array_almost_equal(est, true_pos, decimal=2)

    def test_insufficient_anchors_returns_none(self, cfg, anchor_positions):
        from rtls_algorithms import WLS
        wls = WLS(anchor_positions, cfg.positioning.wls)
        # 앵커 2개만 제공 (min=3)
        dists = {"A2": 5.0, "A3": 8.0}
        assert wls.estimate(dists) is None

    def test_max_jump_clipping(self, cfg, anchor_positions):
        """최대 이동 거리 클리핑 동작 확인."""
        from rtls_algorithms import WLS
        wls = WLS(anchor_positions, cfg.positioning.wls)

        # 첫 번째 추정
        pos1 = np.array([7.5, 6.25])
        d1 = {ak: float(np.linalg.norm(pos1 - av)) for ak, av in anchor_positions.items()}
        wls.estimate(d1)

        # 멀리 떨어진 위치 → 클리핑 발생
        pos2 = np.array([14.9, 12.4])
        d2 = {ak: float(np.linalg.norm(pos2 - av)) for ak, av in anchor_positions.items()}
        est2 = wls.estimate(d2)
        assert est2 is not None
        # 이동 거리가 max_jump_m 이하여야 함
        assert float(np.linalg.norm(est2 - pos1)) <= cfg.positioning.wls.max_jump_m + 0.01

    def test_reset(self, cfg, anchor_positions):
        from rtls_algorithms import WLS
        wls = WLS(anchor_positions, cfg.positioning.wls)
        pos = np.array([7.5, 6.25])
        dists = {ak: float(np.linalg.norm(pos - av)) for ak, av in anchor_positions.items()}
        wls.estimate(dists)
        wls.reset()
        # 리셋 후 prev가 없으므로 jump 클리핑 없음
        assert wls._prev is None


# ──────────────────────────────────────────────────────────────
# AdaptiveEKF tests
# ──────────────────────────────────────────────────────────────

class TestAdaptiveEKF:
    def test_init_and_get_pos(self, cfg, anchor_positions):
        from rtls_algorithms import AdaptiveEKF
        ekf = AdaptiveEKF(anchor_positions, cfg.positioning.ekf)
        assert not ekf.initialized

        pos = np.array([7.5, 6.25])
        ekf.init(pos)
        assert ekf.initialized
        np.testing.assert_array_almost_equal(ekf.get_pos(), pos)

    def test_predict_moves_state(self, cfg, anchor_positions):
        from rtls_algorithms import AdaptiveEKF
        ekf = AdaptiveEKF(anchor_positions, cfg.positioning.ekf)
        ekf.init(np.array([0.0, 0.0]))

        # 속도 수동 설정 (내부 접근)
        with ekf._lock:
            ekf._x[2, 0] = 1.0  # vx = 1 m/s
        ekf.predict(dt=1.0)
        pos = ekf.get_pos()
        assert pos[0] == pytest.approx(1.0, abs=0.01)

    def test_update_converges(self, cfg, anchor_positions):
        """반복 업데이트 시 실제 위치에 수렴하는지 확인."""
        from rtls_algorithms import AdaptiveEKF
        ekf = AdaptiveEKF(anchor_positions, cfg.positioning.ekf)

        true_pos = np.array([7.5, 6.25])
        ekf.init(true_pos + np.array([2.0, 2.0]))  # 오프셋으로 초기화

        dists = {
            ak: float(np.linalg.norm(true_pos - av))
            for ak, av in anchor_positions.items()
        }

        for _ in range(30):
            ekf.predict()
            ekf.update(dists)

        pos = ekf.get_pos()
        assert np.linalg.norm(pos - true_pos) < 0.5

    def test_mahalanobis_gating(self, cfg, anchor_positions):
        """이상값(outlier)이 EKF 업데이트에서 제외되는지 확인."""
        from rtls_algorithms import AdaptiveEKF
        ekf = AdaptiveEKF(anchor_positions, cfg.positioning.ekf)
        ekf.init(np.array([7.5, 6.25]))

        # 정상 데이터로 수렴
        true_pos = np.array([7.5, 6.25])
        dists_ok = {ak: float(np.linalg.norm(true_pos - av)) for ak, av in anchor_positions.items()}
        for _ in range(10):
            ekf.predict()
            ekf.update(dists_ok)

        pos_before = ekf.get_pos().copy()

        # 극단적 이상값
        dists_bad = {ak: 50.0 for ak in anchor_positions}
        ekf.predict()
        ekf.update(dists_bad)

        pos_after = ekf.get_pos()
        # 이상값은 게이팅으로 제외되어 위치 변화가 작아야 함
        assert np.linalg.norm(pos_after - pos_before) < 2.0

    def test_speed_clipping(self, cfg, anchor_positions):
        from rtls_algorithms import AdaptiveEKF
        ekf = AdaptiveEKF(anchor_positions, cfg.positioning.ekf)
        ekf.init(np.array([7.5, 6.25]))

        with ekf._lock:
            ekf._x[2, 0] = 100.0  # 비현실적 속도
            ekf._x[3, 0] = 100.0

        ekf.predict()
        assert ekf.speed() <= cfg.positioning.ekf.max_speed_m_s + 0.01

    def test_adaptive_r_decreases_for_stable(self, cfg, anchor_positions):
        """안정적 측정이 반복될 때 적응형 R이 수렴하는지 확인."""
        from rtls_algorithms import AdaptiveEKF
        ekf = AdaptiveEKF(anchor_positions, cfg.positioning.ekf)
        ekf.init(np.array([7.5, 6.25]))

        true_pos = np.array([7.5, 6.25])
        dists = {ak: float(np.linalg.norm(true_pos - av)) for ak, av in anchor_positions.items()}

        r_vals = []
        for _ in range(50):
            ekf.predict()
            ekf.update(dists)
            r_vals.append(ekf.current_R())

        # R이 합리적 범위 내에 있어야 함
        assert 1e-4 < r_vals[-1] < 10.0

    def test_reset(self, cfg, anchor_positions):
        from rtls_algorithms import AdaptiveEKF
        ekf = AdaptiveEKF(anchor_positions, cfg.positioning.ekf)
        ekf.init(np.array([7.5, 6.25]))
        ekf.reset()
        assert not ekf.initialized

    def test_thread_safety(self, cfg, anchor_positions):
        """predict/update/get_pos 동시 호출 안전성."""
        from rtls_algorithms import AdaptiveEKF
        ekf = AdaptiveEKF(anchor_positions, cfg.positioning.ekf)
        ekf.init(np.array([7.5, 6.25]))

        true_pos = np.array([7.5, 6.25])
        dists = {ak: float(np.linalg.norm(true_pos - av)) for ak, av in anchor_positions.items()}
        errors = []

        def worker():
            for _ in range(100):
                try:
                    ekf.predict()
                    ekf.update(dists)
                    ekf.get_pos()
                except Exception as e:
                    errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for t in threads: t.start()
        for t in threads: t.join()
        assert not errors, f"Thread safety errors: {errors}"


# ──────────────────────────────────────────────────────────────
# AnchorGrouper tests
# ──────────────────────────────────────────────────────────────

class TestAnchorGrouper:
    def test_group_completes_with_min_anchors(self):
        from rtls_core import AnchorGrouper
        g = AnchorGrouper(window_sec=1.0, min_anchors=3)
        now = time.monotonic()
        g.push("A2", "TAG1", 5.0, now)
        g.push("A3", "TAG1", 8.0, now)
        g.push("A4", "TAG1", 7.0, now)

        assert not g.completed.empty()
        grp = g.completed.get_nowait()
        assert grp["tag"] == "TAG1"
        assert set(grp["dists"].keys()) == {"A2", "A3", "A4"}

    def test_incomplete_group_not_queued(self):
        from rtls_core import AnchorGrouper
        g = AnchorGrouper(window_sec=1.0, min_anchors=3)
        now = time.monotonic()
        g.push("A2", "TAG1", 5.0, now)
        g.push("A3", "TAG1", 8.0, now)
        # A4 없음
        assert g.completed.empty()

    def test_stale_data_not_grouped(self):
        from rtls_core import AnchorGrouper
        g = AnchorGrouper(window_sec=0.1, min_anchors=3)
        old = time.monotonic() - 1.0  # 오래된 타임스탬프
        g.push("A2", "TAG1", 5.0, old)
        g.push("A3", "TAG1", 8.0, old)

        now = time.monotonic()
        g.push("A4", "TAG1", 7.0, now)  # 신선한 데이터 1개만
        assert g.completed.empty()

    def test_separate_tags_independent(self):
        from rtls_core import AnchorGrouper
        g = AnchorGrouper(window_sec=1.0, min_anchors=3)
        now = time.monotonic()
        for tag in ["TAG1", "TAG2"]:
            g.push("A2", tag, 5.0, now)
            g.push("A3", tag, 8.0, now)
            g.push("A4", tag, 7.0, now)

        assert g.total_groups == 2

    def test_thread_safety(self):
        from rtls_core import AnchorGrouper
        g = AnchorGrouper(window_sec=0.5, min_anchors=3)
        errors = []

        def pusher(anchor: str):
            for _ in range(50):
                try:
                    g.push(anchor, "TAG1", 5.0, time.monotonic())
                    time.sleep(0.001)
                except Exception as e:
                    errors.append(e)

        threads = [
            threading.Thread(target=pusher, args=("A2",)),
            threading.Thread(target=pusher, args=("A3",)),
            threading.Thread(target=pusher, args=("A4",)),
        ]
        for t in threads: t.start()
        for t in threads: t.join()
        assert not errors


# ──────────────────────────────────────────────────────────────
# ConnManager tests
# ──────────────────────────────────────────────────────────────

class TestConnManager:
    def test_initial_status_waiting(self):
        from rtls_core import ConnManager, TagStatus
        cm = ConnManager(["TAG1", "TAG2"], timeout_sec=5.0)
        assert cm.status("TAG1") == TagStatus.WAITING

    def test_mark_changes_status(self):
        from rtls_core import ConnManager, TagStatus
        cm = ConnManager(["TAG1"], timeout_sec=5.0)
        cm.mark("TAG1")
        assert cm.status("TAG1") == TagStatus.CONNECTED
        assert cm.is_active("TAG1")

    def test_timeout_detection(self):
        from rtls_core import ConnManager, TagStatus
        cm = ConnManager(["TAG1"], timeout_sec=0.1)
        cm.mark("TAG1")
        time.sleep(0.2)
        disc, recon = cm.tick()
        assert cm.status("TAG1") == TagStatus.TIMEOUT
        assert "TAG1" in disc

    def test_elapsed_before_mark(self):
        from rtls_core import ConnManager
        cm = ConnManager(["TAG1"], timeout_sec=5.0)
        assert cm.elapsed("TAG1") == -1.0

    def test_thread_safety(self):
        from rtls_core import ConnManager
        cm = ConnManager(["TAG1", "TAG2"], timeout_sec=10.0)
        errors = []

        def marker():
            for _ in range(200):
                try:
                    cm.mark("TAG1")
                    cm.mark("TAG2")
                except Exception as e:
                    errors.append(e)

        def checker():
            for _ in range(200):
                try:
                    cm.is_active("TAG1")
                    cm.summary
                except Exception as e:
                    errors.append(e)

        threads = [threading.Thread(target=marker),
                   threading.Thread(target=checker),
                   threading.Thread(target=checker)]
        for t in threads: t.start()
        for t in threads: t.join()
        assert not errors


# ──────────────────────────────────────────────────────────────
# parse_line tests
# ──────────────────────────────────────────────────────────────

class TestParseLine:
    def test_valid_line(self, cfg):
        from rtls_core import parse_line
        line = "TAG:0064 DIST:5000 ANCHOR:0002"
        result = parse_line(line, "A2", cfg)
        assert result is not None
        tag, dist = result
        assert tag == "TAG1"
        assert dist == pytest.approx(5.0)

    def test_wrong_anchor_ignored(self, cfg):
        from rtls_core import parse_line
        # A3 데이터를 A2 수신기에서 받은 경우
        line = "TAG:0064 DIST:5000 ANCHOR:0003"
        result = parse_line(line, "A2", cfg)
        assert result is None

    def test_invalid_format(self, cfg):
        from rtls_core import parse_line
        line = "garbage data line"
        assert parse_line(line, "A2", cfg) is None

    def test_distance_mm_to_m_conversion(self, cfg):
        from rtls_core import parse_line
        line = "TAG:0064 DIST:9500 ANCHOR:0002"
        result = parse_line(line, "A2", cfg)
        assert result is not None
        _, dist = result
        assert dist == pytest.approx(9.5)

    def test_distance_exceeds_max(self, cfg):
        from rtls_core import parse_line
        line = "TAG:0064 DIST:99000 ANCHOR:0002"  # 99m > 22m
        result = parse_line(line, "A2", cfg)
        assert result is None

    def test_unknown_tag_gets_fallback_name(self, cfg):
        from rtls_core import parse_line
        line = "TAG:FFFF DIST:5000 ANCHOR:0002"
        result = parse_line(line, "A2", cfg)
        assert result is not None
        tag, _ = result
        assert tag.startswith("TAG_")


# ──────────────────────────────────────────────────────────────
# TagTracker integration test
# ──────────────────────────────────────────────────────────────

class TestTagTracker:
    def test_pipeline_produces_position(self, cfg, anchor_positions):
        from rtls_algorithms import HeightCorrector
        from rtls_core import TagTracker

        hcorr = HeightCorrector(cfg)
        room_bounds = (np.array([0.0, 0.0]), np.array([15.0, 12.5]))
        tracker = TagTracker("TAG1", cfg, anchor_positions, hcorr, room_bounds)

        true_pos = np.array([7.5, 6.25])

        # 충분한 반복으로 파이프라인 실행
        for _ in range(40):
            for ak, av in anchor_positions.items():
                d = float(np.linalg.norm(true_pos - av))
                tracker.push_distance(ak, d)
            tracker.compute()
            tracker.lerp()

        fp = tracker.get_fused_pos()
        assert fp is not None, "Position should be estimated after sufficient updates"
        assert np.linalg.norm(fp - true_pos) < 1.5

    def test_reset_clears_state(self, cfg, anchor_positions):
        from rtls_algorithms import HeightCorrector
        from rtls_core import TagTracker

        hcorr   = HeightCorrector(cfg)
        bounds  = (np.array([0.0, 0.0]), np.array([15.0, 12.5]))
        tracker = TagTracker("TAG1", cfg, anchor_positions, hcorr, bounds)

        true_pos = np.array([7.5, 6.25])
        for _ in range(20):
            for ak, av in anchor_positions.items():
                tracker.push_distance(ak, float(np.linalg.norm(true_pos - av)))
            tracker.compute()

        tracker.reset()
        assert tracker.get_fused_pos() is None
        assert tracker.get_smooth_pos() is None
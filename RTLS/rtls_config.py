"""
rtls_config.py — Configuration loader & validated data models
=============================================================
RTLS System v2.0.0

외부 YAML 파일을 읽어 타입 안전한 dataclass로 변환합니다.
코드에 하드코딩된 설정값을 모두 제거하고
런타임 검증(validation)을 수행합니다.

Usage:
    cfg = RTLSConfig.from_yaml("config.yaml")
    pos = cfg.anchor_position("A2")   # np.ndarray
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import yaml

log = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# Connection sub-configs
# ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SerialConnection:
    port: str
    baud: int = 115200

    def validate(self) -> None:
        if not self.port:
            raise ValueError("Serial port must not be empty.")
        if self.baud <= 0:
            raise ValueError(f"Invalid baud rate: {self.baud}")


@dataclass(frozen=True)
class TCPConnection:
    host: str
    port: int

    def validate(self) -> None:
        if not self.host:
            raise ValueError("TCP host must not be empty.")
        if not (1 <= self.port <= 65535):
            raise ValueError(f"Invalid TCP port: {self.port}")


# ──────────────────────────────────────────────────────────────
# Anchor config
# ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AnchorConfig:
    name: str
    x: float
    y: float
    height: float
    connection: SerialConnection | TCPConnection

    @property
    def position_2d(self) -> np.ndarray:
        return np.array([self.x, self.y], dtype=float)

    def validate(self) -> None:
        if self.height < 0:
            raise ValueError(
                f"Anchor {self.name}: height must be >= 0, got {self.height}"
            )
        self.connection.validate()


# ──────────────────────────────────────────────────────────────
# Algorithm sub-configs
# ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class HeightCorrectionConfig:
    enabled: bool = True


@dataclass(frozen=True)
class WLSConfig:
    max_jump_m: float = 4.0
    outlier_threshold_m: float = 1.5
    dist_buffer_size: int = 8


@dataclass(frozen=True)
class EKFConfig:
    process_noise: tuple = (0.05, 0.05, 0.20, 0.20)
    measurement_noise: float = 0.25
    init_covariance: float = 2.0
    dt: float = 0.1
    adaptive_r: bool = True
    adaptive_r_window: int = 10
    max_speed_m_s: float = 5.0

    @property
    def Q(self) -> np.ndarray:
        return np.diag(self.process_noise)

    def validate(self) -> None:
        if len(self.process_noise) != 4:
            raise ValueError("EKF process_noise must have exactly 4 elements.")
        if self.measurement_noise <= 0:
            raise ValueError("EKF measurement_noise must be > 0.")
        if self.dt <= 0:
            raise ValueError("EKF dt must be > 0.")


@dataclass(frozen=True)
class PositioningConfig:
    min_anchors: int = 3
    group_window_sec: float = 0.15
    max_dist_m: float = 22.0
    dist_valid_age_sec: float = 0.8
    height_correction: HeightCorrectionConfig = field(
        default_factory=HeightCorrectionConfig
    )
    wls: WLSConfig = field(default_factory=WLSConfig)
    ekf: EKFConfig = field(default_factory=EKFConfig)

    def validate(self) -> None:
        if self.min_anchors < 2:
            raise ValueError("min_anchors must be >= 2.")
        if self.group_window_sec <= 0:
            raise ValueError("group_window_sec must be > 0.")
        self.ekf.validate()


@dataclass(frozen=True)
class ConnectionConfig:
    tag_timeout_sec: float = 5.0
    reconnect_sec: float = 5.0
    tcp_timeout_sec: float = 3.0


@dataclass(frozen=True)
class SimulatorConfig:
    move_duration_sec: float = 8.0
    stop_duration_sec: float = 5.0
    noise_moving_m: float = 0.08
    noise_stopped_m: float = 0.03


@dataclass(frozen=True)
class VisualizationConfig:
    update_interval_ms: int = 100
    anchor_colors: Dict[str, str] = field(default_factory=dict)
    tag_colors: Dict[str, str] = field(default_factory=dict)


# ──────────────────────────────────────────────────────────────
# Root config
# ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class RTLSConfig:
    """
    RTLS 시스템 전체 설정.
    config.yaml을 파싱하여 생성하며 런타임 검증을 포함합니다.
    """
    version: str
    simulation_mode: bool
    log_dir: str
    log_level: str

    anchors: Dict[str, AnchorConfig]
    anchor_hw_map: Dict[str, str]   # "0002" → "A2"
    tag_hw_map: Dict[str, str]      # "0064" → "TAG1"
    tag_height: float

    positioning: PositioningConfig
    connection: ConnectionConfig
    visualization: VisualizationConfig
    simulator: SimulatorConfig

    # ── 편의 접근자 ──────────────────────────────────────────

    def anchor_position(self, name: str) -> np.ndarray:
        return self.anchors[name].position_2d

    def anchor_positions(self) -> Dict[str, np.ndarray]:
        return {name: a.position_2d for name, a in self.anchors.items()}

    def anchor_height(self, name: str) -> float:
        return self.anchors[name].height

    def tag_ids(self) -> list[str]:
        return list(self.tag_hw_map.values())

    # ── YAML 파싱 팩토리 ─────────────────────────────────────

    @classmethod
    def from_yaml(cls, path: str | Path) -> "RTLSConfig":
        """
        YAML 파일을 읽어 RTLSConfig를 생성합니다.

        Args:
            path: config.yaml 경로

        Returns:
            검증된 RTLSConfig 인스턴스

        Raises:
            FileNotFoundError: 파일 없을 때
            ValueError: 설정값 유효성 오류
        """
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Config not found: {p.resolve()}")

        with p.open(encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        cfg = cls._parse(raw)
        cfg._validate()
        log.info(f"[Config] Loaded from {p.resolve()}")
        return cfg

    @classmethod
    def _parse(cls, raw: dict) -> "RTLSConfig":
        sys_raw = raw.get("system", {})
        hw_map  = raw.get("hardware_map", {})
        vis_raw = raw.get("visualization", {})
        sim_raw = raw.get("simulator", {})
        pos_raw = raw.get("positioning", {})
        con_raw = raw.get("connection", {})
        tags_raw= raw.get("tags", {})

        anchors = cls._parse_anchors(raw.get("anchors", {}))

        pos_cfg = cls._parse_positioning(pos_raw)
        ekf_cfg = pos_cfg.ekf  # noqa: F841 (used via pos_cfg)

        return cls(
            version         = sys_raw.get("version", "2.0.0"),
            simulation_mode = bool(sys_raw.get("simulation_mode", False)),
            log_dir         = sys_raw.get("log_dir", "./rtls_logs"),
            log_level       = sys_raw.get("log_level", "INFO"),
            anchors         = anchors,
            anchor_hw_map   = {
                k: v for k, v in hw_map.get("anchors", {}).items()
            },
            tag_hw_map      = {
                k: v for k, v in hw_map.get("tags", {}).items()
            },
            tag_height      = float(tags_raw.get("height", 1.0)),
            positioning     = pos_cfg,
            connection      = ConnectionConfig(
                tag_timeout_sec = float(con_raw.get("tag_timeout_sec", 5.0)),
                reconnect_sec   = float(con_raw.get("reconnect_sec", 5.0)),
                tcp_timeout_sec = float(con_raw.get("tcp_timeout_sec", 3.0)),
            ),
            visualization   = VisualizationConfig(
                update_interval_ms = int(vis_raw.get("update_interval_ms", 100)),
                anchor_colors      = vis_raw.get("anchor_colors", {}),
                tag_colors         = vis_raw.get("tag_colors", {}),
            ),
            simulator       = SimulatorConfig(
                move_duration_sec  = float(sim_raw.get("move_duration_sec", 8.0)),
                stop_duration_sec  = float(sim_raw.get("stop_duration_sec", 5.0)),
                noise_moving_m     = float(sim_raw.get("noise_moving_m", 0.08)),
                noise_stopped_m    = float(sim_raw.get("noise_stopped_m", 0.03)),
            ),
        )

    @staticmethod
    def _parse_anchors(raw: dict) -> Dict[str, AnchorConfig]:
        anchors: Dict[str, AnchorConfig] = {}
        for name, acfg in raw.items():
            conn_raw = acfg.get("connection", {})
            conn_type = conn_raw.get("type", "serial")
            if conn_type == "serial":
                conn = SerialConnection(
                    port = conn_raw.get("port", "/dev/ttyACM0"),
                    baud = int(conn_raw.get("baud", 115200)),
                )
            elif conn_type == "tcp":
                conn = TCPConnection(
                    host = conn_raw["host"],
                    port = int(conn_raw["port"]),
                )
            else:
                raise ValueError(f"Unknown connection type: {conn_type}")

            anchors[name] = AnchorConfig(
                name       = name,
                x          = float(acfg["x"]),
                y          = float(acfg["y"]),
                height     = float(acfg["height"]),
                connection = conn,
            )
        return anchors

    @staticmethod
    def _parse_positioning(raw: dict) -> PositioningConfig:
        ekf_raw = raw.get("ekf", {})
        wls_raw = raw.get("wls", {})
        hc_raw  = raw.get("height_correction", {})

        proc_noise = ekf_raw.get(
            "process_noise", [0.05, 0.05, 0.20, 0.20]
        )

        return PositioningConfig(
            min_anchors       = int(raw.get("min_anchors", 3)),
            group_window_sec  = float(raw.get("group_window_sec", 0.15)),
            max_dist_m        = float(raw.get("max_dist_m", 22.0)),
            dist_valid_age_sec= float(raw.get("dist_valid_age_sec", 0.8)),
            height_correction = HeightCorrectionConfig(
                enabled = bool(hc_raw.get("enabled", True))
            ),
            wls = WLSConfig(
                max_jump_m          = float(wls_raw.get("max_jump_m", 4.0)),
                outlier_threshold_m = float(
                    wls_raw.get("outlier_threshold_m", 1.5)),
                dist_buffer_size    = int(wls_raw.get("dist_buffer_size", 8)),
            ),
            ekf = EKFConfig(
                process_noise    = tuple(proc_noise),
                measurement_noise= float(ekf_raw.get("measurement_noise", 0.25)),
                init_covariance  = float(ekf_raw.get("init_covariance", 2.0)),
                dt               = float(ekf_raw.get("dt", 0.1)),
                adaptive_r       = bool(ekf_raw.get("adaptive_r", True)),
                adaptive_r_window= int(ekf_raw.get("adaptive_r_window", 10)),
                max_speed_m_s    = float(ekf_raw.get("max_speed_m_s", 5.0)),
            ),
        )

    def _validate(self) -> None:
        if not self.anchors:
            raise ValueError("No anchors defined in config.")
        for a in self.anchors.values():
            a.validate()
        if not self.tag_hw_map:
            raise ValueError("No tags defined in hardware_map.tags.")
        self.positioning.validate()
        log.debug(
            f"[Config] Validated: {len(self.anchors)} anchors,"
            f" {len(self.tag_hw_map)} tags"
        )
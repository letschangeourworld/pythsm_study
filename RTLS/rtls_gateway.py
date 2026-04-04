"""
rtls_gateway.py — Main Gateway: orchestration & visualization
=============================================================
RTLS System v2.0.0

실행:
    python3 rtls_gateway.py                      # config.yaml (기본)
    python3 rtls_gateway.py --config my.yaml
    python3 rtls_gateway.py --simulate           # 시뮬레이션 모드 강제
    python3 rtls_gateway.py --config my.yaml --log-level DEBUG

연결 구조:
    앵커2 Pi ─ USB /dev/ttyACM0 ──── 앵커2 (직접)
             ─ TCP → 앵커3 Pi  ───── 앵커3 (원격)
             ─ TCP → 앵커4 Pi  ───── 앵커4 (원격)
"""

from __future__ import annotations

import argparse
import logging
import os
import queue
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import matplotlib
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import warnings
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle, Polygon as MplPolygon
from matplotlib.path import Path as MplPath
from matplotlib.widgets import Button
from scipy.spatial import ConvexHull

from rtls_algorithms import HeightCorrector
from rtls_config import RTLSConfig, SerialConnection, TCPConnection
from rtls_core import (
    AnchorGrouper,
    ConnManager,
    SerialReceiver,
    TagStatus,
    TagTracker,
    TCPReceiver,
)

warnings.filterwarnings("ignore")


# ──────────────────────────────────────────────────────────────
# 로깅 설정
# ──────────────────────────────────────────────────────────────

def _setup_logging(log_dir: str, level: str) -> None:
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_file = Path(log_dir) / f"rtls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)-8s] %(name)s — %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    logging.getLogger(__name__).info("Log → %s", log_file)


# ──────────────────────────────────────────────────────────────
# 공간 기하 (RoomGeometry)
# ──────────────────────────────────────────────────────────────

class RoomGeometry:
    """앵커 좌표로부터 공간 경계를 계산합니다."""

    _MARGIN_RATIO = 0.12

    def __init__(self, anchor_positions: Dict[str, np.ndarray]) -> None:
        pts = np.array(list(anchor_positions.values()))
        self.min_x = pts[:, 0].min()
        self.max_x = pts[:, 0].max()
        self.min_y = pts[:, 1].min()
        self.max_y = pts[:, 1].max()
        self.W = self.max_x - self.min_x
        self.H = self.max_y - self.min_y
        margin = max(self.W, self.H) * self._MARGIN_RATIO
        self.XLIM = (self.min_x - margin, self.max_x + margin)
        self.YLIM = (self.min_y - margin, self.max_y + margin)
        self.MARGIN = margin
        self.center = pts.mean(axis=0)

        try:
            hull = ConvexHull(pts)
            self.hull_verts = pts[hull.vertices]
        except Exception:
            self.hull_verts = pts

        self.hull_path = MplPath(
            np.vstack([self.hull_verts, self.hull_verts[0]])
        )
        self.min_pos = np.array([self.min_x, self.min_y])
        self.max_pos = np.array([self.max_x, self.max_y])

    def clip(self, p: np.ndarray) -> np.ndarray:
        return np.clip(p, self.min_pos, self.max_pos)

    def patch(self, **kwargs) -> MplPolygon:
        return MplPolygon(self.hull_verts, closed=True, **kwargs)


# ──────────────────────────────────────────────────────────────
# 시뮬레이터
# ──────────────────────────────────────────────────────────────

class Simulator:
    """
    하드웨어 없이 동작을 검증하기 위한 내장 시뮬레이터.
    실제 앵커/태그 움직임을 모사하고 가우시안 노이즈를 추가합니다.
    """

    def __init__(
        self,
        grouper: AnchorGrouper,
        conn_mgr: ConnManager,
        room: RoomGeometry,
        hcorr: HeightCorrector,
        cfg: RTLSConfig,
    ) -> None:
        self._grouper    = grouper
        self._conn_mgr   = conn_mgr
        self._room       = room
        self._hcorr      = hcorr
        self._cfg        = cfg
        self._sim_cfg    = cfg.simulator
        self._t          = 0.0
        self._move_t:    Dict[str, float] = {t: 0.0 for t in cfg.tag_ids()}
        self._stop_pos:  Dict[str, Optional[np.ndarray]] = {
            t: None for t in cfg.tag_ids()
        }
        self._running    = False
        self.tag_enabled: Dict[str, bool] = {t: True for t in cfg.tag_ids()}

    def _cycle(self) -> tuple[bool, float]:
        sc = self._sim_cfg
        cycle = sc.move_duration_sec + sc.stop_duration_sec
        phase = self._t % cycle
        moving = phase < sc.move_duration_sec
        return moving, phase

    def _true_pos(self, tid: str, moving: bool) -> np.ndarray:
        sc = self._sim_cfg
        cx, cy = self._room.center
        hw = self._room.W * 0.35
        hh = self._room.H * 0.35
        mt = self._move_t[tid]

        if tid == list(self._cfg.tag_ids())[0]:
            p = np.array([cx + hw * np.cos(mt * 0.3), cy + hh * np.sin(mt * 0.3)])
        else:
            p = np.array([cx + hw * 0.5 * np.sin(mt * 0.25), cy + hh * 0.5 * np.cos(mt * 0.25)])

        p = self._room.clip(p)
        if moving:
            self._stop_pos[tid] = p.copy()
            return p
        if self._stop_pos[tid] is None:
            self._stop_pos[tid] = p.copy()
        return self._stop_pos[tid].copy()

    def _run(self) -> None:
        dt = self._cfg.positioning.ekf.dt
        sc = self._sim_cfg
        anchor_positions = self._cfg.anchor_positions()

        while self._running:
            self._t += dt
            moving, _ = self._cycle()

            for tid in self._cfg.tag_ids():
                if not self.tag_enabled.get(tid, True):
                    continue
                if moving:
                    self._move_t[tid] += dt
                pos   = self._true_pos(tid, moving)
                noise = sc.noise_moving_m if moving else sc.noise_stopped_m
                ts    = time.monotonic()

                for ak, av in anchor_positions.items():
                    dz   = self._hcorr.dz(ak)
                    d_2d = np.linalg.norm(pos - av)
                    d_3d = float(np.sqrt(d_2d ** 2 + dz ** 2)
                                 + np.random.normal(0, noise))
                    d_3d = max(0.1, d_3d)
                    d_h  = self._hcorr.correct(ak, d_3d)
                    self._grouper.push(ak, tid, d_h, ts)

                self._conn_mgr.mark(tid)
            time.sleep(dt)

    def start(self) -> None:
        self._running = True
        threading.Thread(target=self._run, daemon=True, name="simulator").start()
        logging.getLogger(__name__).info("[Simulator] Started")

    def stop(self) -> None:
        self._running = False


# ──────────────────────────────────────────────────────────────
# 색상 / 스타일 상수
# ──────────────────────────────────────────────────────────────

_C = dict(
    BG_FIG="#F4F6F9", BG_AX="#EFF3F8",
    BG_HDR="#0D1B2A", BG_PANEL="#FFFFFF",
    GRID="#D0D4DA", SPINE="#AAAAAA",
    TEXT="#1A1A2E", SUB="#555566", BORDER="#CCCCDD",
)


# ──────────────────────────────────────────────────────────────
# 메인 게이트웨이
# ──────────────────────────────────────────────────────────────

class RTLSGateway:
    """
    RTLS 시스템 메인 오케스트레이터.

    - 설정 로드 (RTLSConfig)
    - 수신기 초기화 (Serial / TCP / Simulator)
    - 위치 추정 파이프라인 구동
    - matplotlib 실시간 시각화
    """

    _DRAIN_MAX = 100    # 프레임당 최대 처리 그룹 수
    _DIAG_PERIOD = 30   # 진단 출력 주기 (프레임)

    def __init__(self, cfg: RTLSConfig) -> None:
        self._log = logging.getLogger(self.__class__.__name__)
        self._cfg = cfg

        self._log.info("=" * 60)
        self._log.info("  RTLS Gateway v2.0.0")
        self._log.info("  simulation=%s  anchors=%s  tags=%s",
                       cfg.simulation_mode,
                       list(cfg.anchors.keys()),
                       cfg.tag_ids())
        self._log.info("=" * 60)

        # 공간 기하
        anchor_positions = cfg.anchor_positions()
        self._room    = RoomGeometry(anchor_positions)
        room_bounds   = (self._room.min_pos, self._room.max_pos)

        # 핵심 컴포넌트
        self._hcorr   = HeightCorrector(cfg)
        self._grouper = AnchorGrouper(
            cfg.positioning.group_window_sec,
            cfg.positioning.min_anchors,
        )
        self._conn_mgr = ConnManager(
            cfg.tag_ids(),
            cfg.connection.tag_timeout_sec,
        )
        self._trackers: Dict[str, TagTracker] = {
            tid: TagTracker(tid, cfg, anchor_positions, self._hcorr, room_bounds)
            for tid in cfg.tag_ids()
        }

        # 수신기
        self._receivers: Dict[str, SerialReceiver | TCPReceiver] = {}
        self._sim: Optional[Simulator] = None

        self._t0         = time.monotonic()
        self._frame_cnt  = 0
        self._show_circles = True
        self._show_wls   = True

        self._setup_receivers()
        self._setup_figure()
        self._start_flush_loop()

    # ── 수신기 설정 ──────────────────────────────────────────

    def _setup_receivers(self) -> None:
        if self._cfg.simulation_mode:
            self._sim = Simulator(
                self._grouper, self._conn_mgr,
                self._room, self._hcorr, self._cfg,
            )
            self._sim.start()
            return

        for anchor_name, anchor_cfg in self._cfg.anchors.items():
            conn = anchor_cfg.connection
            if isinstance(conn, SerialConnection):
                r = SerialReceiver(
                    anchor_name, conn,
                    self._grouper, self._conn_mgr,
                    self._hcorr, self._cfg,
                )
                self._log.info("  %s → USB %s", anchor_name, conn.port)
            elif isinstance(conn, TCPConnection):
                r = TCPReceiver(
                    anchor_name, conn,
                    self._grouper, self._conn_mgr,
                    self._hcorr, self._cfg,
                )
                self._log.info("  %s → TCP %s:%d", anchor_name, conn.host, conn.port)
            else:
                self._log.error("Unknown connection type for %s", anchor_name)
                continue

            r.start()
            self._receivers[anchor_name] = r

    def _start_flush_loop(self) -> None:
        def _loop():
            while True:
                time.sleep(1.0)
                self._grouper.flush_stale()
        threading.Thread(target=_loop, daemon=True, name="flush-loop").start()

    # ── 시각화 설정 ──────────────────────────────────────────

    def _setup_figure(self) -> None:
        plt.rcParams.update({
            "figure.facecolor": _C["BG_FIG"],
            "axes.facecolor":   _C["BG_AX"],
            "axes.edgecolor":   _C["SPINE"],
            "axes.labelcolor":  _C["TEXT"],
            "xtick.color":      _C["SUB"],
            "ytick.color":      _C["SUB"],
            "text.color":       _C["TEXT"],
            "grid.color":       _C["GRID"],
            "grid.linestyle":   "--",
            "grid.alpha":       0.6,
        })

        self._fig = plt.figure(figsize=(20, 10), facecolor=_C["BG_FIG"])
        gs = gridspec.GridSpec(
            3, 1, figure=self._fig,
            height_ratios=[0.08, 0.84, 0.08], hspace=0.0,
        )

        self._build_header(gs[0])

        gm = gridspec.GridSpecFromSubplotSpec(
            1, 2, subplot_spec=gs[1], width_ratios=[1.7, 1.0], wspace=0.03,
        )
        self._ax_map = self._fig.add_subplot(gm[0])

        gt = gridspec.GridSpecFromSubplotSpec(
            1, len(self._cfg.tag_ids()), subplot_spec=gm[1], wspace=0.04,
        )
        self._ax_tags:   Dict[str, plt.Axes] = {}
        self._txt_info:  Dict[str, plt.Text] = {}
        self._badge_con: Dict[str, plt.Text] = {}

        for i, tid in enumerate(self._cfg.tag_ids()):
            col  = self._cfg.visualization.tag_colors.get(tid, "#1565C0")
            ax_t = self._fig.add_subplot(gt[i])
            ax_t.set_facecolor(_C["BG_PANEL"])
            ax_t.set_axis_off()
            for s in ax_t.spines.values():
                s.set_visible(True)
                s.set_color(_C["BORDER"])
                s.set_linewidth(1.2)

            ax_t.axhspan(0.91, 1.0, facecolor=col, alpha=0.85, zorder=0)
            ax_t.text(0.50, 0.955, f"◉  {tid}",
                      ha="center", va="center", fontsize=12, fontweight="bold",
                      color="white", transform=ax_t.transAxes, zorder=2)
            self._badge_con[tid] = ax_t.text(
                0.50, 0.50, "WAITING...", ha="center", va="center",
                fontsize=10, fontweight="bold", color="#999",
                transform=ax_t.transAxes, zorder=3,
            )
            self._txt_info[tid] = ax_t.text(
                0.05, 0.88, "", transform=ax_t.transAxes,
                ha="left", va="top", fontsize=8.5, color=_C["TEXT"],
                fontfamily="monospace", linespacing=1.55, zorder=2,
            )
            self._ax_tags[tid] = ax_t

        # 상태 바
        ax_st = self._fig.add_subplot(gs[2])
        ax_st.set_axis_off()
        ax_st.add_patch(plt.Rectangle(
            (0, 0), 1, 1, transform=ax_st.transAxes,
            facecolor="#FFFDE7", zorder=0,
        ))
        self._st_txt = ax_st.text(
            0.50, 0.52, "", ha="center", va="center",
            fontsize=9.5, color=_C["TEXT"], transform=ax_st.transAxes, zorder=1,
        )

        self._setup_buttons()
        self._init_map()

    def _build_header(self, ss) -> None:
        ax = self._fig.add_subplot(ss)
        ax.set_facecolor(_C["BG_HDR"])
        ax.set_axis_off()
        cfg = self._cfg
        mode = "SIMULATION" if cfg.simulation_mode else "HARDWARE"
        anchors = list(cfg.anchors.keys())
        ax.text(0.50, 0.75,
                f"DWM3001CDK RTLS Gateway v2.0.0  |  {mode}"
                f"  |  앵커{anchors}  |  태그{cfg.tag_ids()}  |  WLS+AdaptiveEKF",
                ha="center", va="center", fontsize=11, fontweight="bold",
                color="#FFFFFF", transform=ax.transAxes)
        ax.text(0.50, 0.28,
                f"GroupWin={cfg.positioning.group_window_sec*1000:.0f}ms"
                f"  MinAnc={cfg.positioning.min_anchors}"
                f"  HCorr={'ON' if cfg.positioning.height_correction.enabled else 'OFF'}"
                f"  TagH={cfg.tag_height:.1f}m"
                f"  AdaptiveR={'ON' if cfg.positioning.ekf.adaptive_r else 'OFF'}",
                ha="center", va="center", fontsize=8.5, color="#B0BEC5",
                transform=ax.transAxes)

    def _setup_buttons(self) -> None:
        axes_params = [
            ([0.68, 0.005, 0.09, 0.042], "Circles: ON",  "#E3F2FD", "#0D47A1", self._toggle_circles),
            ([0.78, 0.005, 0.075, 0.042], "WLS: ON",      "#FFF3E0", "#E65100", self._toggle_wls),
            ([0.865, 0.005, 0.09, 0.042],
             "HCorr: ON" if self._cfg.positioning.height_correction.enabled else "HCorr: OFF",
             "#FCE4EC", "#880E4F", self._toggle_hcorr),
        ]
        self._btn_circ = self._btn_wls = self._btn_hc = None
        btns = []
        for rect, label, color, fcolor, cb in axes_params:
            ax_b = self._fig.add_axes(rect)
            btn  = Button(ax_b, label, color=color, hovercolor="#BBDEFB")
            btn.label.set_fontsize(9)
            btn.label.set_color(fcolor)
            btn.label.set_fontweight("bold")
            btn.on_clicked(cb)
            btns.append(btn)
        self._btn_circ, self._btn_wls, self._btn_hc = btns

    def _toggle_circles(self, _) -> None:
        self._show_circles = not self._show_circles
        self._btn_circ.label.set_text(
            "Circles: ON" if self._show_circles else "Circles: OFF"
        )
        if not self._show_circles:
            for tid in self._cfg.tag_ids():
                for c in self._range_circles[tid].values():
                    c.set_visible(False)
        self._fig.canvas.draw_idle()

    def _toggle_wls(self, _) -> None:
        self._show_wls = not self._show_wls
        self._btn_wls.label.set_text("WLS: ON" if self._show_wls else "WLS: OFF")
        if not self._show_wls:
            for tid in self._cfg.tag_ids():
                self._dot_wls[tid].set_visible(False)
        self._fig.canvas.draw_idle()

    def _toggle_hcorr(self, _) -> None:
        self._hcorr.enabled = not self._hcorr.enabled
        self._btn_hc.label.set_text(
            "HCorr: ON" if self._hcorr.enabled else "HCorr: OFF"
        )
        for tr in self._trackers.values():
            tr.reset()
        self._fig.canvas.draw_idle()

    def _init_map(self) -> None:
        ax = self._ax_map
        r  = self._room
        cfg= self._cfg
        anchor_positions = cfg.anchor_positions()

        ax.set_facecolor(_C["BG_AX"])
        ax.set_xlim(*r.XLIM)
        ax.set_ylim(*r.YLIM)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("X (m)", fontsize=11, color=_C["TEXT"])
        ax.set_ylabel("Y (m)", fontsize=11, color=_C["TEXT"])
        ax.set_title(
            f"위치 지도  |  앵커{list(anchor_positions.keys())}"
            f"  |  WLS + AdaptiveEKF",
            fontsize=12, fontweight="bold", color=_C["TEXT"], pad=8,
        )
        ax.tick_params(colors=_C["SUB"], labelsize=9)
        for sp in ax.spines.values():
            sp.set_color(_C["SPINE"])
        ax.grid(True, lw=0.8)
        ax.add_patch(r.patch(
            facecolor="#DDEEFF", edgecolor="#1565C0",
            lw=2.0, alpha=0.35, zorder=1,
        ))
        self._draw_dims()

        for ak, av in anchor_positions.items():
            ac   = cfg.visualization.anchor_colors.get(ak, "#888888")
            h    = cfg.anchor_height(ak)
            conn = cfg.anchors[ak].connection
            lbl  = "USB" if isinstance(conn, SerialConnection) else conn.host
            ax.scatter(*av, s=420, marker="^", color=ac, zorder=10,
                       edgecolors="#222", lw=1.5)
            ax.annotate(
                f" {ak}\n({av[0]:.0f},{av[1]:.0f})\nh={h:.1f}m\n[{lbl}]",
                av, color=ac, fontsize=8.5, fontweight="bold",
                xytext=(8, 5), textcoords="offset points", zorder=11,
            )

        self._dot:          Dict[str, plt.Line2D] = {}
        self._dot_wls:      Dict[str, plt.Line2D] = {}
        self._range_circles: Dict[str, Dict[str, Circle]] = {
            tid: {} for tid in cfg.tag_ids()
        }

        for tid in cfg.tag_ids():
            col = cfg.visualization.tag_colors.get(tid, "#1565C0")
            self._dot[tid], = ax.plot(
                [], [], "o", color=col, ms=16, zorder=22,
                markeredgecolor="#111", markeredgewidth=1.8,
                label=f"{tid} EKF", visible=False,
            )
            self._dot_wls[tid], = ax.plot(
                [], [], "D", color="#888888", ms=7, zorder=19,
                markeredgecolor="#444", markeredgewidth=1.0,
                alpha=0.80, visible=False, label=f"{tid} WLS",
            )
            for ak, av in anchor_positions.items():
                ac = cfg.visualization.anchor_colors.get(ak, "#888888")
                c  = Circle(av, radius=0.0, fill=False, linestyle="--",
                            linewidth=1.0, alpha=0.35, edgecolor=ac,
                            visible=False, zorder=5)
                ax.add_patch(c)
                self._range_circles[tid][ak] = c

        self._update_legend()

    def _update_legend(self) -> None:
        handles, labels = [], []
        for tid in self._cfg.tag_ids():
            if tid in self._dot:
                handles.append(self._dot[tid])
                labels.append(f"{tid} EKF")
            if tid in self._dot_wls and self._show_wls:
                handles.append(self._dot_wls[tid])
                labels.append(f"{tid} WLS")
        if handles:
            self._ax_map.legend(
                handles, labels, loc="lower right",
                fontsize=9, facecolor="white",
                edgecolor=_C["SPINE"], framealpha=0.95,
            )

    def _draw_dims(self) -> None:
        r, ax = self._room, self._ax_map
        mg = r.MARGIN * 0.5
        yd = r.min_y - mg
        ax.annotate("", xy=(r.max_x, yd), xytext=(r.min_x, yd),
                    arrowprops=dict(arrowstyle="<->", color=_C["SUB"], lw=1.4))
        ax.text((r.min_x + r.max_x) / 2, yd - mg * 0.3,
                f"{r.W:.1f} m", ha="center", va="top", color=_C["SUB"], fontsize=10)
        xd = r.max_x + mg
        ax.annotate("", xy=(xd, r.max_y), xytext=(xd, r.min_y),
                    arrowprops=dict(arrowstyle="<->", color=_C["SUB"], lw=1.4))
        ax.text(xd + mg * 0.2, (r.min_y + r.max_y) / 2,
                f"{r.H:.1f} m", ha="left", va="center",
                color=_C["SUB"], fontsize=10, rotation=90)

    # ── 메인 루프 ─────────────────────────────────────────────

    def _drain(self) -> int:
        consumed = 0
        while consumed < self._DRAIN_MAX:
            try:
                grp = self._grouper.completed.get_nowait()
            except queue.Empty:
                break

            tag   = grp["tag"]
            dists = grp["dists"]
            if tag not in self._trackers:
                continue
            for ak, d in dists.items():
                self._trackers[tag].push_distance(ak, d)
            consumed += 1

        disc, recon = self._conn_mgr.tick()
        for t in disc:
            self._log.warning("[Sys] %s disconnected", t)
            if t in self._trackers:
                self._trackers[t].reset()
        for t in recon:
            self._log.info("[Sys] %s reconnected", t)

        self._frame_cnt += 1
        if self._frame_cnt % self._DIAG_PERIOD == 1:
            self._print_diag(consumed)

        return consumed

    def _print_diag(self, consumed: int) -> None:
        elapsed = time.monotonic() - self._t0
        self._log.info("=" * 60)
        self._log.info(
            "[DIAG] t=%.1fs frame=%d consumed=%d groups=%d HCorr=%s",
            elapsed, self._frame_cnt, consumed,
            self._grouper.total_groups,
            "ON" if self._hcorr.enabled else "OFF",
        )
        if not self._cfg.simulation_mode:
            for ak, r in self._receivers.items():
                self._log.info(
                    "  [%s] %s  rx=%d",
                    ak, "✓ connected" if r.connected else "✗ disconnected",
                    r.rx_count,
                )
        for tid in self._cfg.tag_ids():
            tr  = self._trackers[tid]
            fp  = tr.get_fused_pos()
            st  = self._conn_mgr.status(tid).name
            ekf_r = tr._ekf.current_R()
            if fp is not None:
                self._log.info(
                    "  [%s] (%.3f, %.3f)m  spd=%.3f  EKF_R=%.4f  err=%d  [%s]",
                    tid, fp[0], fp[1], tr.speed(), ekf_r, tr.get_err_count(), st,
                )
                for ak, (meas, pred, err) in tr.get_residuals().items():
                    flag = " !!!" if abs(err) > 1.0 else (" !" if abs(err) > 0.5 else "")
                    self._log.info(
                        "    Resid %s: meas=%.3f pred=%.3f err=%+.3f%s",
                        ak, meas, pred, err, flag,
                    )
            else:
                self._log.info("  [%s] not initialized [%s]", tid, st)
        self._log.info("=" * 60)

    def _compute(self) -> None:
        for tr in self._trackers.values():
            tr.compute()
            tr.lerp()

    def _redraw(self) -> None:
        elapsed = time.monotonic() - self._t0
        cfg     = self._cfg
        stat    = []

        # 앵커 수신기 상태
        if not cfg.simulation_mode:
            anchor_status = "  ".join(
                f"{ak}:{'✓' if r.connected else '✗'}"
                for ak, r in self._receivers.items()
            )
        else:
            anchor_status = "SIM"

        anchor_positions = cfg.anchor_positions()

        for tid in cfg.tag_ids():
            tr        = self._trackers[tid]
            is_active = self._conn_mgr.is_active(tid)
            status    = self._conn_mgr.status(tid)

            if not is_active:
                for dot in [self._dot.get(tid), self._dot_wls.get(tid)]:
                    if dot: dot.set_visible(False)
                for c in self._range_circles.get(tid, {}).values():
                    c.set_visible(False)
                bdg = self._badge_con.get(tid)
                if bdg:
                    msg = ("WAITING..." if status == TagStatus.WAITING
                           else f"NO SIGNAL ({self._conn_mgr.elapsed(tid):.0f}s)")
                    bdg.set_text(msg)
                    bdg.set_color("#999" if status == TagStatus.WAITING else "#CC3333")
                    bdg.set_visible(True)
                if tid in self._txt_info:
                    self._txt_info[tid].set_text("")
                stat.append(f"{tid}:{status.name[:4]}")
                continue

            sp_pos  = tr.get_smooth_pos()
            wls_pos = tr.get_wls_pos()
            fp      = tr.get_fused_pos()

            bdg = self._badge_con.get(tid)
            if bdg: bdg.set_visible(False)

            if sp_pos is not None:
                self._dot[tid].set_data([sp_pos[0]], [sp_pos[1]])
                self._dot[tid].set_visible(True)
            else:
                self._dot[tid].set_visible(False)

            if wls_pos is not None and self._show_wls:
                self._dot_wls[tid].set_data([wls_pos[0]], [wls_pos[1]])
                self._dot_wls[tid].set_visible(True)
            else:
                self._dot_wls[tid].set_visible(False)

            for ak, av in anchor_positions.items():
                circ  = self._range_circles[tid].get(ak)
                if circ is None: continue
                df    = tr.get_dist_filt()
                dv    = df.get(ak)
                fresh = tr.is_dist_fresh(ak)
                if self._show_circles and is_active and dv is not None and fresh:
                    circ.center = av
                    circ.set_radius(dv)
                    circ.set_visible(True)
                else:
                    circ.set_visible(False)

            info_txt = self._txt_info.get(tid)
            if fp is not None and info_txt:
                dist_filt = tr.get_dist_filt()
                residuals = tr.get_residuals()
                d_rows = ""
                for ak in anchor_positions:
                    dv    = dist_filt.get(ak, 0.0) or 0.0
                    fresh = "✓" if tr.is_dist_fresh(ak) else "!"
                    res   = residuals.get(ak)
                    err_s = f"{res[2]:+.2f}" if res else "  N/A"
                    dz    = self._hcorr.dz(ak)
                    conn  = cfg.anchors[ak].connection
                    src   = "USB" if isinstance(conn, SerialConnection) else "TCP"
                    d_rows += f" {ak}[{src}]: {dv:5.2f}m  R{err_s}  dz{dz:.1f} [{fresh}]\n"

                txt = (
                    f" X  : {fp[0]:>7.3f} m\n"
                    f" Y  : {fp[1]:>7.3f} m\n"
                    f" Spd: {tr.speed():>7.4f} m/s\n"
                    f" EKFstd: {tr.pos_std():>6.4f} m\n"
                    f" AdaptR: {tr._ekf.current_R():.4f}\n"
                    f" Err: {tr.get_err_count()}\n"
                    f" ──────────────────────\n"
                    f" 거리(수평) R=잔차:\n"
                    f"{d_rows}"
                    f" ──────────────────────\n"
                    f" HCorr:{'ON' if self._hcorr.enabled else 'OFF'}"
                    f"  G={self._grouper.total_groups}"
                )
                info_txt.set_text(txt)
                stat.append(f"{tid}:({fp[0]:.2f},{fp[1]:.2f})")
            elif info_txt:
                info_txt.set_text(" 초기화 중...")

        grp = self._grouper.total_groups
        cs  = self._conn_mgr.summary
        body = (
            f"  |  ".join(stat) if stat else "대기 중..."
        )
        self._st_txt.set_text(
            f"t={elapsed:.1f}s  앵커[{anchor_status}]  Groups={grp}  {body}  [{cs}]"
        )

    def _update(self, _) -> list:
        self._drain()
        self._compute()
        self._redraw()
        return []

    def run(self) -> None:
        self._fig.subplots_adjust(
            left=0.05, right=0.985, top=0.998, bottom=0.055, hspace=0.0,
        )
        self._ani = FuncAnimation(
            self._fig, self._update,
            interval=self._cfg.visualization.update_interval_ms,
            blit=False, cache_frame_data=False,
        )
        plt.show()


# ──────────────────────────────────────────────────────────────
# matplotlib 백엔드 선택
# ──────────────────────────────────────────────────────────────

def _select_backend() -> str:
    try:
        name = get_ipython().__class__.__name__  # type: ignore[name-defined]
        if name in ("ZMQInteractiveShell", "TerminalInteractiveShell"):
            return "inline"
    except NameError:
        pass
    if sys.platform.startswith("linux") and not os.environ.get("DISPLAY"):
        return "Agg"
    return "TkAgg"


# ──────────────────────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="RTLS Gateway v2.0.0 — DWM3001CDK Real-Time Location System",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--config", type=str, default="config.yaml",
        help="YAML 설정 파일 경로",
    )
    parser.add_argument(
        "--simulate", action="store_true",
        help="시뮬레이션 모드 강제 활성화 (config 값 무시)",
    )
    parser.add_argument(
        "--log-level", type=str, default=None,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="로그 레벨 (config 값 오버라이드)",
    )
    args = parser.parse_args()

    # 설정 로드
    cfg = RTLSConfig.from_yaml(args.config)

    # CLI 오버라이드
    if args.simulate:
        # simulation_mode는 frozen dataclass라 새 인스턴스로 교체
        import dataclasses
        cfg = dataclasses.replace(cfg, simulation_mode=True)

    log_level = args.log_level or cfg.log_level
    _setup_logging(cfg.log_dir, log_level)

    log = logging.getLogger(__name__)

    if not cfg.simulation_mode:
        log.info("")
        log.info("  ※ 원격 Pi에서 먼저 실행:")
        for ak, anchor_cfg in cfg.anchors.items():
            conn = anchor_cfg.connection
            if isinstance(conn, TCPConnection):
                log.info(
                    "    [앵커%s Pi] python3 rtls_agent.py --anchor %s --port %d",
                    ak, ak, conn.port,
                )
        log.info("")

    matplotlib.use(_select_backend())

    RTLSGateway(cfg).run()


if __name__ == "__main__":
    main()
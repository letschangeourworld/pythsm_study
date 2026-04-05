"""
rtls_agent.py — Remote Anchor Agent
====================================
RTLS System v2.0.0

앵커3, 앵커4가 연결된 원격 Pi에서 실행합니다.
USB 시리얼로 DWM3001CDK 앵커를 읽어 게이트웨이 Pi로 TCP 전송합니다.

실행:
    python3 rtls_agent.py --anchor A3 --port 9003
    python3 rtls_agent.py --anchor A4 --port 9004 --serial /dev/ttyACM1

게이트웨이에서 접속:
    앵커3 Pi IP:9003
    앵커4 Pi IP:9004

설계 원칙:
    - TCP 서버 소켓: 게이트웨이의 접속을 기다립니다 (passive open)
    - 게이트웨이가 재접속하면 자동으로 새 세션을 시작합니다
    - 시리얼 연결이 끊기면 RECONNECT_SEC 후 재시도합니다
    - 포맷 필터: "TAG:xxxx DIST:dddd ANCHOR:yyyy" 패턴만 전송합니다
"""

from __future__ import annotations

import argparse
import logging
import re
import socket
import sys
import time
import threading
from typing import Optional

# ── 로그 설정 ─────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)-8s] %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("AGENT")

try:
    import serial
except ImportError:
    log.error("pyserial 미설치 — pip install pyserial")
    sys.exit(1)

# ── 설정 상수 ─────────────────────────────────────────────────
DEFAULT_SERIAL_PORT  = "/dev/ttyACM0"
DEFAULT_BAUD_RATE    = 115_200
TCP_HOST             = "0.0.0.0"   # 모든 인터페이스 수신
RECONNECT_SEC        = 5.0
SERIAL_READ_INTERVAL = 0.001       # 시리얼 폴링 간격 (s)
LOG_SAMPLE_EVERY     = 100         # N번째 수신마다 DEBUG 출력

# 유효 라인 패턴 (TAG:xxxx DIST:dddd ANCHOR:yyyy)
_VALID_LINE_RE = re.compile(
    r"TAG[:\s]*[0-9A-Fa-f]+"
    r".*?DIST[:\s]*\d+"
    r".*?ANCHOR[:\s]*[0-9A-Fa-f]+",
    re.IGNORECASE,
)


# ──────────────────────────────────────────────────────────────
# Agent 클래스
# ──────────────────────────────────────────────────────────────

class AnchorAgent:
    """
    단일 앵커 에이전트.

    동작 흐름:
        1. TCP 서버 소켓을 열고 게이트웨이 접속 대기
        2. 접속 수락 후 시리얼 포트 열기
        3. 시리얼 → TCP 실시간 전달 (유효 라인만)
        4. 연결 끊김 시 세션 종료 후 1로 돌아감
    """

    def __init__(
        self,
        anchor_name: str,
        tcp_port: int,
        serial_port: str = DEFAULT_SERIAL_PORT,
        baud_rate: int   = DEFAULT_BAUD_RATE,
    ) -> None:
        self.anchor_name = anchor_name
        self.tcp_port    = tcp_port
        self.serial_port = serial_port
        self.baud_rate   = baud_rate

        # 통계 (진단용)
        self._rx_count   = 0
        self._tx_count   = 0
        self._err_count  = 0

    # ── Public ───────────────────────────────────────────────

    def run(self) -> None:
        """에이전트 메인 루프. Ctrl+C로 종료합니다."""
        log.info("[%s] Agent v2.0.0 시작", self.anchor_name)
        log.info("  시리얼: %s @ %d baud", self.serial_port, self.baud_rate)
        log.info("  TCP 수신 대기: %s:%d", TCP_HOST, self.tcp_port)

        srv = self._create_server_socket()

        try:
            while True:
                log.info("[%s] 게이트웨이 접속 대기 중...", self.anchor_name)
                try:
                    conn, addr = srv.accept()
                except OSError as e:
                    log.error("[%s] accept 오류: %s", self.anchor_name, e)
                    time.sleep(1.0)
                    continue

                log.info("[%s] 게이트웨이 접속: %s", self.anchor_name, addr)
                conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

                self._run_session(conn)
        finally:
            srv.close()

    # ── Internal ─────────────────────────────────────────────

    def _create_server_socket(self) -> socket.socket:
        """재사용 가능한 TCP 서버 소켓을 생성합니다."""
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            srv.bind((TCP_HOST, self.tcp_port))
        except OSError as e:
            log.error("[%s] 포트 %d 바인딩 실패: %s", self.anchor_name, self.tcp_port, e)
            sys.exit(1)
        srv.listen(1)
        return srv

    def _run_session(self, conn: socket.socket) -> None:
        """
        게이트웨이 연결이 유지되는 동안 시리얼 → TCP 전달을 수행합니다.
        연결이 끊기거나 시리얼 오류 시 세션을 종료합니다.
        """
        ser: Optional[serial.Serial] = None
        try:
            ser = self._open_serial()
            if ser is None:
                return  # 시리얼 열기 실패 (게이트웨이에 None 알림 없이 종료)

            log.info("[%s] 세션 시작 — 스트리밍 중...", self.anchor_name)

            while True:
                if not ser.in_waiting:
                    time.sleep(SERIAL_READ_INTERVAL)
                    continue

                try:
                    raw  = ser.readline()
                    line = raw.decode("utf-8", errors="ignore").strip()
                    self._rx_count += 1

                    if not _VALID_LINE_RE.search(line):
                        continue

                    msg = (line + "\n").encode("utf-8")
                    conn.sendall(msg)
                    self._tx_count += 1

                    if self._tx_count % LOG_SAMPLE_EVERY == 1:
                        log.debug(
                            "[%s] tx #%d: %s",
                            self.anchor_name, self._tx_count, line,
                        )

                except serial.SerialException as e:
                    log.warning("[%s] 시리얼 오류: %s", self.anchor_name, e)
                    break
                except (BrokenPipeError, ConnectionResetError):
                    log.warning("[%s] 게이트웨이 연결 끊김 (전송 중)", self.anchor_name)
                    break
                except Exception as e:
                    self._err_count += 1
                    if self._err_count % 50 == 1:
                        log.error("[%s] 처리 오류: %s", self.anchor_name, e)

        except (BrokenPipeError, ConnectionResetError):
            log.warning("[%s] 게이트웨이 연결 끊김", self.anchor_name)
        except Exception as e:
            log.error("[%s] 세션 오류: %s", self.anchor_name, e)
        finally:
            if ser:
                try: ser.close()
                except Exception: pass
            try: conn.close()
            except Exception: pass
            log.info(
                "[%s] 세션 종료 — rx=%d tx=%d err=%d",
                self.anchor_name, self._rx_count, self._tx_count, self._err_count,
            )

    def _open_serial(self) -> Optional[serial.Serial]:
        """
        시리얼 포트를 엽니다. 실패하면 RECONNECT_SEC 후 재시도합니다.
        게이트웨이가 이미 연결된 상태이므로 빠르게 열어야 합니다.

        Returns:
            serial.Serial 인스턴스, 또는 None (외부 중단 시)
        """
        while True:
            try:
                ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
                log.info("[%s] 시리얼 연결됨: %s", self.anchor_name, self.serial_port)
                return ser
            except serial.SerialException as e:
                log.warning(
                    "[%s] 시리얼 열기 실패: %s — %.1fs 후 재시도",
                    self.anchor_name, e, RECONNECT_SEC,
                )
                time.sleep(RECONNECT_SEC)


# ──────────────────────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="RTLS Anchor Agent v2.0.0 — 원격 Pi 앵커 데이터 전달",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--anchor", type=str, required=True,
        metavar="NAME",
        help="앵커 이름 (예: A3)",
    )
    parser.add_argument(
        "--port", type=int, required=True,
        metavar="PORT",
        help="TCP 수신 포트 (예: 9003)",
    )
    parser.add_argument(
        "--serial", type=str, default=DEFAULT_SERIAL_PORT,
        metavar="DEVICE",
        help="시리얼 포트 경로",
    )
    parser.add_argument(
        "--baud", type=int, default=DEFAULT_BAUD_RATE,
        metavar="RATE",
        help="시리얼 보드레이트",
    )
    args = parser.parse_args()

    if not (1 <= args.port <= 65535):
        log.error("유효하지 않은 포트: %d", args.port)
        sys.exit(1)

    agent = AnchorAgent(
        anchor_name = args.anchor,
        tcp_port    = args.port,
        serial_port = args.serial,
        baud_rate   = args.baud,
    )

    try:
        agent.run()
    except KeyboardInterrupt:
        log.info("[%s] 사용자 종료 (Ctrl+C)", args.anchor)


if __name__ == "__main__":
    main()
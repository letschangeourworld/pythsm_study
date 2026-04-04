# DWM3001CDK RTLS System v2.0.0

> **Real-Time Location System** — UWB 기반 산업용 실내 위치 추적 시스템
> DWM3001CDK 앵커 + Raspberry Pi 구성 | WLS + Adaptive EKF 융합 알고리즘

---

## 목차

1. [시스템 개요](#시스템-개요)
2. [아키텍처](#아키텍처)
3. [요구 사항](#요구-사항)
4. [설치](#설치)
5. [빠른 시작 (시뮬레이션)](#빠른-시작-시뮬레이션)
6. [하드웨어 배포](#하드웨어-배포)
7. [설정 가이드 (config.yaml)](#설정-가이드)
8. [알고리즘 상세](#알고리즘-상세)
9. [테스트 실행](#테스트-실행)
10. [디렉토리 구조](#디렉토리-구조)
11. [문제 해결](#문제-해결)

---

## 시스템 개요

DWM3001CDK UWB 모듈을 앵커로 사용해 최대 2개 태그의 실내 위치를 실시간으로 추정합니다.

| 항목 | 사양 |
|------|------|
| 앵커 수 | 3~4개 (확장 가능) |
| 태그 수 | 최대 2개 (설정 변경으로 확장) |
| 위치 정확도 | 10~30 cm (환경에 따라 다름) |
| 갱신 주기 | ~100 ms |
| 통신 방식 | USB Serial (앵커2) + TCP Socket (앵커3, 4) |
| 위치 알고리즘 | WLS + Adaptive EKF |
| 높이 보정 | 앵커/태그 높이 차이 기반 3D→2D 변환 |

---

## 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│ 게이트웨이 Pi (앵커2) │
│ │
│ rtls_gateway.py │
│ ┌─────────────┐ ┌──────────────┐ ┌───────────────────┐ │
│ │SerialReceiver│ │ TCPReceiver │ │ TCPReceiver │ │
│ │ (A2:USB) │ │ (A3:TCP) │ │ (A4:TCP) │ │
│ └──────┬──────┘ └──────┬───────┘ └────────┬──────────┘ │
│ └────────────────┼────────────────── │ │
│ ▼ │
│ AnchorGrouper │
│ (타임윈도우 기반 데이터 묶음) │
│ │ │
│ ┌───────────▼──────────┐ │
│ │ TagTracker │ │
│ │ DistKF → WLS → EKF │ │
│ └───────────┬──────────┘ │
│ │ │
│ Visualization │
│ (matplotlib FuncAnimation) │
└─────────────────────────────────────────────────────────────┘
▲ ▲
USB Serial TCP Socket
│ │
┌─────┴─────┐ ┌────────┴──────────┐
│ 앵커2 │ │ 앵커3 Pi / 앵커4 Pi│
│ DWM3001 │ │ rtls_agent.py │
└───────────┘ └───────────────────┘
```

### 데이터 파이프라인

```
측정 거리 (mm)
│
▼
[HeightCorrector] 3D 측정거리 → 2D 수평거리 (√(d²-dz²))
│
▼
[DistKF] 1D 칼만 필터로 거리 스무딩
│
▼
[WLS] Weighted Least Squares 초기 위치 추정
│
▼
[AdaptiveEKF] 적응형 EKF 위치+속도 추정
│ - Innovation Covariance Matching (R 적응)
│ - Mahalanobis 게이팅 (이상값 제외)
│ - Joseph form 공분산 업데이트
▼
[LERP] 위치 스무딩 (시각화용)
```

---

## 요구 사항

### 소프트웨어

- Python 3.10+
- 의존성 패키지:

```txt
numpy>=1.24
scipy>=1.10
matplotlib>=3.7
pyserial>=3.5
pyyaml>=6.0
pytest>=7.4 # 테스트 실행 시
pytest-timeout>=2.1
```

### 하드웨어

- Raspberry Pi 4 × 3대 (앵커 Pi)
- DWM3001CDK UWB 모듈 × 3개 이상
- 동일 네트워크 (Wi-Fi 또는 유선)

---

## 설치

```bash
# 저장소 클론
git clone https://github.com/yourorg/rtls-system.git
cd rtls-system

# 가상환경 생성 (권장)
python3 -m venv .venv
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

---

## 빠른 시작 (시뮬레이션)

하드웨어 없이 동작을 즉시 확인합니다.

```bash
# config.yaml에서 simulation_mode: true 설정 후
python3 rtls_gateway.py --simulate
```

또는:

```yaml
# config.yaml
system:
simulation_mode: true
```

```bash
python3 rtls_gateway.py
```

시뮬레이터는 두 태그가 설정된 공간에서 궤적을 그리며 움직입니다.
WLS(회색 다이아몬드)와 EKF(색상 원) 출력을 실시간으로 비교할 수 있습니다.

---

## 하드웨어 배포

### 1단계: 앵커 Pi 설정 (앵커3, 앵커4)

각 원격 Pi에 에이전트를 배포합니다:

```bash
# 앵커3 Pi에서
python3 rtls_agent.py --anchor A3 --port 9003

# 앵커4 Pi에서
python3 rtls_agent.py --anchor A4 --port 9004
```

에이전트는 USB 시리얼로 DWM3001CDK를 읽어 TCP로 게이트웨이에 전달합니다.

### 2단계: config.yaml 수정

```yaml
anchors:
A3:
connection:
type: tcp
host: "192.168.1.103" # ← 앵커3 Pi의 실제 IP로 변경
port: 9003
A4:
connection:
type: tcp
host: "192.168.1.104" # ← 앵커4 Pi의 실제 IP로 변경
port: 9004
```

### 3단계: 앵커 좌표 측정 및 설정

현장에서 줄자로 앵커 위치를 측정해 설정합니다:

```yaml
anchors:
A2:
x: 0.0 # m (기준점)
y: 12.5 # m
height: 2.5 # m (바닥에서 앵커까지)
```

### 4단계: 게이트웨이 실행

```bash
python3 rtls_gateway.py --config config.yaml
```

---

## 설정 가이드

`config.yaml`의 주요 파라미터 설명입니다.

### 위치 추정 파라미터

```yaml
positioning:
min_anchors: 3 # 위치 계산에 필요한 최소 앵커 수
group_window_sec: 0.15 # 그룹핑 타임윈도우 (초)
# 좁히면 응답 빠름, 넓히면 그룹 성공률 향상
max_dist_m: 22.0 # 유효 거리 상한 (환경에 맞게 조정)

height_correction:
enabled: true # 앵커 높이가 모두 같으면 false로 설정 가능

wls:
max_jump_m: 4.0 # 프레임 간 최대 이동 허용 (고속 태그면 값 증가)
outlier_threshold_m: 1.5 # 아웃라이어 제거 임계값

ekf:
process_noise: [0.05, 0.05, 0.20, 0.20]
# [x, y, vx, vy] 순서
# 환경이 불안정하면 x,y 값을 키움
# 태그가 빠르게 움직이면 vx,vy 값을 키움

measurement_noise: 0.25 # 초기 R 값 (adaptive_r: true면 자동 조정)
adaptive_r: true # 환경 변화 시 R 자동 추적 (권장)
max_speed_m_s: 5.0 # 태그 최대 속도 물리적 제약
```

### 로그 레벨 조정

```yaml
system:
log_level: "INFO" # DEBUG: 모든 파싱/그룹핑 로그
# INFO: 연결 이벤트, 진단 요약
# WARNING: 연결 끊김, 타임아웃만
```

---

## 알고리즘 상세

### Adaptive EKF (Innovation Covariance Matching)

기존 고정 R 값 대신, 실시간 잔차(innovation) 통계를 이용해 측정 노이즈 공분산 R을 동적으로 추정합니다.

```
R̂ = α·R + (1-α)·(ε̂ - (S - R))
```

- ε̂: 최근 N개 잔차 제곱의 평균
- S: Innovation covariance
- α = 0.95 (지수이동평균 계수)

효과: 멀티패스, 환경 변화, 센서 열화 시 자동으로 R이 증가해 견고성이 향상됩니다.

### Mahalanobis 게이팅

각 측정값의 통계적 이상도를 계산해 임계값(chi²=10.83, p=0.999)을 초과하면 업데이트에서 제외합니다.

```
d_M² = (z - ẑ)² / S < threshold
```

효과: 반사파, 오측정, 장애물 통과 신호로 인한 위치 급변을 방지합니다.

### Joseph Form 공분산 업데이트

수치 안정성을 위해 표준 P = (I-KH)P 대신 Joseph form을 사용합니다:

```
P = (I-KH)P(I-KH)ᵀ + KRKᵀ
```

반복 업데이트 시 공분산 행렬의 양정치성(positive definiteness)이 유지됩니다.

---

## 테스트 실행

```bash
# 전체 테스트 실행
pytest tests/ -v

# 특정 모듈 테스트
pytest tests/test_rtls.py::TestAdaptiveEKF -v

# 커버리지 측정
pip install pytest-cov
pytest tests/ --cov=. --cov-report=html
```

### 테스트 항목

| 모듈 | 테스트 케이스 |
|------|-------------|
| RTLSConfig | YAML 파싱, 유효성 검사, 연결 타입 확인 |
| HeightCorrector | 보정 정확도, 비활성화, 스레드 안전성 |
| DistKF | 스무딩 효과, 신선도 판단, 리셋 |
| WLS | 위치 수렴, 최소 앵커 검사, 점프 클리핑 |
| AdaptiveEKF | 수렴성, Mahalanobis 게이팅, 적응형 R, 스레드 안전성 |
| AnchorGrouper | 그룹 완성, 오래된 데이터 필터링, 스레드 안전성 |
| ConnManager | 상태 전이, 타임아웃, 스레드 안전성 |
| parse_line | 정상 파싱, 앵커 검증, 거리 변환 |
| TagTracker | 전체 파이프라인 통합 테스트 |

---

## 디렉토리 구조

```
rtls/
├── config.yaml # 시스템 설정 (여기만 수정)
├── rtls_gateway.py # 메인 진입점 (실행 파일)
├── rtls_config.py # 설정 로더 & 데이터 모델
├── rtls_algorithms.py # 신호처리 알고리즘 (HeightCorrector, DistKF, WLS, EKF)
├── rtls_core.py # 데이터 파이프라인 (Grouper, Tracker, Receiver)
├── rtls_agent.py # 원격 Pi 에이전트 (앵커3, 앵커4)
├── requirements.txt # Python 의존성
├── rtls_logs/ # 자동 생성 로그 디렉토리
└── tests/
└── test_rtls.py # 단위 테스트 (pytest)
```

---

## 문제 해결

### 위치가 계산되지 않음

- `DEBUG` 모드로 로그 확인: `--log-level DEBUG`
- 그룹 카운터가 증가하는지 확인 (`Groups=N` 상태 바)
- `GROUP_WINDOW_SEC`를 늘려 봄 (예: 0.15 → 0.30)
- 앵커 연결 상태 확인 (`앵커[A2:✓ A3:✓ A4:✓]`)

### 위치가 튀거나 불안정함

- `adaptive_r: true` 활성화 확인
- `outlier_threshold_m` 값을 줄임 (예: 1.5 → 1.0)
- 앵커 좌표가 정확한지 재측정
- `height_correction.enabled: true` 및 앵커 높이 값 확인

### TCP 연결 실패

```bash
# 원격 Pi에서 에이전트 실행 여부 확인
ps aux | grep rtls_agent

# 포트 개방 여부 확인
nc -zv 192.168.1.103 9003

# 방화벽 설정
sudo ufw allow 9003/tcp
```

### 시리얼 포트 권한 오류

```bash
sudo usermod -aG dialout $USER
# 로그아웃 후 재로그인
```

---

## 라이선스

MIT License — 자세한 내용은 `LICENSE` 파일을 참조하세요.
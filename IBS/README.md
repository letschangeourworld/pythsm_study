# 🎧 IBS - Interpretation Broadcast System
## 다국어 실시간 통역 방송 시스템

> **교회/컨퍼런스/행사**에서 실시간 다국어 동시통역 방송을 위한 오픈소스 시스템
> iPhone · Android · PC 모든 기기에서 브라우저만으로 송출 및 청취 가능

---

## 📋 목차

1. [시스템 개요](#시스템-개요)
2. [아키텍처](#아키텍처)
3. [기술 스택](#기술-스택)
4. [설치 및 실행](#설치-및-실행)
5. [포트 구성](#포트-구성)
6. [페이지별 사용법](#페이지별-사용법)
7. [IP 변경 대응](#ip-변경-대응)
8. [주요 기능](#주요-기능)
9. [문제 해결](#문제-해결)

---

## 🌐 시스템 개요

```

\[통역자 (iPhone/PC)\] ─── 🎙️ 음성 송출 ───► \[LiveKit 미디어 서버\]
│
▼ WebRTC (UDP)
\[청취자 (핸드폰/PC)\] ◄─── 🔊 음성 수신 ───────────────┘

\[관리자 (PC/핸드폰)\] ─── 채널 ON/OFF, 채팅, 신규채널 추가 ──► \[FastAPI + WebSocket\]

plaintext

```plaintext

### 주요 특징

| 기능 | 설명 |
|------|------|
| 🎙️ 실시간 음성 방송 | WebRTC 기반 초저지연 음성 전송 |
| 📱 크로스플랫폼 | iPhone Safari · Android · PC Chrome 모두 지원 |
| 🌐 다국어 채널 | 영어·일어·중국어 + 신규 언어 동적 추가 |
| 💬 실시간 채팅 | 카카오톡 스타일 채팅 (관리자 공지 포함) |
| 🎛️ 마이크 선택 | 핸드폰 마이크 / 서버PC 전문마이크 선택 가능 |
| 📊 모니터링 | Prometheus + Grafana 실시간 모니터링 |

---

## 🏗️ 아키텍처

```

┌─────────────────────────────────────────────────────────────┐
│ 클라이언트 │
│ 📱 iPhone(Safari) 💻 PC(Chrome) 🖥️ 서버PC(전문마이크) │
└──────────┬──────────────┬───────────────────┬───────────────┘
│ HTTPS:19443 │ HTTP:19000 │ HTTP:19082
▼ ▼ ▼
┌─────────────────────────────────────────────────────────────┐
│ Nginx (Reverse Proxy) │
│ :19000 메인/청취자 :19443 iOS통역자 :19082 통역자(PC) │
│ /rtc → LiveKit:7880 /api → FastAPI:8000 │
└──────────┬──────────────────────────┬───────────────────────┘
│ │
▼ ▼
┌──────────────────┐ ┌───────────────────────────────────┐
│ LiveKit Server │ │ FastAPI Backend │
│ :7880 신호채널 │ │ /api/v1/livekit/token 토큰발급 │
│ :7881 TCP미디어 │ │ /api/channels 채널관리 │
│ :55000-55100 UDP│ │ /api/broadcast/\* 방송제어 │
│ WebRTC ICE │ │ /ws WebSocket │
└──────────────────┘ └──────────┬────────────────────────┘
│
┌────────────────┼────────────────┐
▼ ▼ ▼
┌──────────┐ ┌──────────┐ ┌──────────────┐
│PostgreSQL│ │ Redis │ │ MinIO │
│ DB:5432 │ │ :6379 │ │ Storage │
└──────────┘ └──────────┘ └──────────────┘
│
┌────────────┼────────────┐
▼ ▼ ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│Prometheus│ │ Grafana │ │ Loki │
│ :9090 │ │ :3000 │ │ 로그 │
└──────────┘ └──────────┘ └──────────┘

plaintext

````plaintext

---

## 🛠️ 기술 스택

| 구분 | 기술 | 버전 | 역할 |
|------|------|------|------|
| **미디어 서버** | LiveKit | 1.13.0 | WebRTC 음성 송출/수신 |
| **백엔드** | FastAPI (Python) | 3.11 | REST API + WebSocket |
| **웹서버** | Nginx | 1.31 | 리버스 프록시 + SSL |
| **DB** | PostgreSQL | 17 + pgvector | 방송 세션 관리 |
| **캐시** | Redis | latest | 실시간 상태 관리 |
| **스토리지** | MinIO | latest | 파일 저장 |
| **인증** | Keycloak | latest | SSO 인증 |
| **모니터링** | Prometheus + Grafana | latest | 시스템 모니터링 |
| **로그** | Loki | latest | 로그 수집 |
| **컨테이너** | Docker Compose | latest | 전체 스택 관리 |

---

## 🚀 설치 및 실행

### 필수 요구사항

- Ubuntu 22.04 / Debian 11 이상
- Docker + Docker Compose
- 최소 RAM 4GB, 저장공간 20GB
- 포트 개방: 19000, 19443, 17880, 17881, 55000-55100 (UDP)

### 1단계: 저장소 클론

```bash
git clone https://github.com/letschangeourworld/pythsm_study.git
cd pythsm_study/IBS
```

### 2단계: 환경변수 설정

```bash
cp .env.example .env
vi .env
```

**.env 주요 설정:**

```env
# 서버 IP (현재 서버의 LAN IP 입력)
SERVER_IP=192.168.0.15

# LiveKit 보안키 (32자 이상)
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_32char_secret_key

# JWT 시크릿 (32자 이상)
JWT_SECRET=your_32char_jwt_secret_key

# 관리자 계정
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_password

# DB 비밀번호
POSTGRES_PASSWORD=your_db_password
REDIS_PASSWORD=your_redis_password
```

### 3단계: SSL 인증서 생성 (로컬망용 자체서명)

```bash
mkdir -p configs/ssl/vitna
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
  -keyout configs/ssl/vitna/key.pem \
  -out configs/ssl/vitna/cert.pem \
  -subj "/CN=localhost"
```

### 4단계: 실행

```bash
docker compose up -d
```

### 5단계: 상태 확인

```bash
docker compose ps
# 모든 서비스 Up (healthy) 확인

# API 정상 확인
curl http://localhost:19000/api/health
```

---

## 🔌 포트 구성

| 포트 | 프로토콜 | 용도 | 접속 대상 |
|------|----------|------|-----------|
| **19000** | HTTP | 메인/청취자/관리자 | 모든 사용자 |
| **19443** | HTTPS | iOS 통역자 전용 | iPhone 통역자 |
| **19080** | HTTP | 관리자 전용 | 관리자 |
| **19081** | HTTP | 청취자 전용 | 청취자 |
| **19082** | HTTP | 통역자(PC) 전용 | PC 통역자 |
| **17880** | TCP | LiveKit 신호채널 | LiveKit SDK |
| **17881** | TCP | LiveKit 미디어 TCP | LiveKit SDK |
| **55000-55100** | **UDP** | LiveKit ICE/미디어 | WebRTC |
| 19300 | HTTP | Grafana 모니터링 | 관리자 |
| 19011 | HTTP | MinIO 스토리지 | 관리자 |

> ⚠️ **UDP 55000-55100 포트 개방 필수** - 방화벽에서 반드시 허용해야 합니다.

---

## 📱 페이지별 사용법

### 1. 메인 페이지 (청취자 입장)
````

[http://서버IP:19000](http://xn--ip-v41jw5m:19000/)

plaintext

```plaintext
- 언어 채널 선택 (영어/일어/중국어)
- ON AIR 상태인 채널만 활성화
- 채널 클릭 → 청취자 페이지로 이동

---

### 2. 청취자 페이지
```

[http://서버IP:19000/listen.html?ch=english](http://xn--ip-v41jw5m:19000/listen.html?ch=english)
[http://서버IP:19000/listen.html?ch=japanese](http://xn--ip-v41jw5m:19000/listen.html?ch=japanese)
[http://서버IP:19000/listen.html?ch=chinese](http://xn--ip-v41jw5m:19000/listen.html?ch=chinese)

plaintext

```plaintext

**사용 순서:**
1. 이어폰 연결 (하울링 방지)
2. 언어 채널 페이지 접속
3. **[청취 시작]** 버튼 클릭
4. 통역 음성 청취 시작 🔊

**기능:**
- 실시간 음성 청취 (WebRTC)
- 카카오톡 스타일 채팅
- 실시간 STT 자막 표시
- 볼륨 조절

---

### 3. 통역자 페이지

**PC 환경:**
```

[http://서버IP:19082/pages/interpreter/index.html](http://xn--ip-v41jw5m:19082/pages/interpreter/index.html)

plaintext

```plaintext

**iPhone/iOS 환경:**
```

[https://서버IP:19443/pages/interpreter/index.html](https://xn--ip-v41jw5m:19443/pages/interpreter/index.html)

plaintext

```plaintext
> ⚠️ iOS는 반드시 HTTPS 접속 필요 (인증서 경고 → '고급' → '방문' 클릭)

**사용 순서:**
1. 상단 **채널 선택** (영어/일어/중국어)
2. **마이크 소스 선택**
   - 📱 내 마이크: 현재 기기 마이크 사용
   - 🖥️ 서버PC 마이크: 전문 마이크 장치 선택
3. **[▶ 방송 시작]** 클릭
4. 방송 중 🔴 표시 확인
5. **[⏹ 방송 종료]** 클릭

---

### 4. 관리자 페이지
```

[http://서버IP:19000/admin.html](http://xn--ip-v41jw5m:19000/admin.html)

plaintext

````plaintext

**기본 계정:** admin / admin123

**주요 기능:**

| 기능 | 설명 |
|------|------|
| 채널 방송 제어 | 토글로 채널 ON/OFF |
| ➕ 채널 추가 | 신규 언어 채널 동적 생성 |
| 방송 생성 | 방송 세션 생성 및 관리 |
| 공지 전송 | 채팅창에 공지 메시지 전송 |
| 채팅 기록 | 채널별 채팅 히스토리 조회 |
| 빠른 링크 | 각 페이지 바로가기 |

---

## 🔄 IP 변경 대응

다른 네트워크(다른 장소)로 이동 시:

```bash
# 자동 IP 감지 및 전체 설정 업데이트
/opt/translation-system/scripts/update-ip.sh
```

**또는 재부팅:**
```bash
sudo reboot
# 부팅 시 자동으로 IP 감지 및 적용
```

**수동 변경 시:**
```bash
# 1. .env 파일 수정
vi .env  # SERVER_IP=새IP

# 2. livekit.yaml 수정
vi configs/livekit/livekit.yaml  # node_ip: 새IP

# 3. 서비스 재시작
docker compose restart livekit api nginx
```

---

## ⭐ 주요 기능

### 🎙️ 마이크 소스 선택
통역자 페이지에서 두 가지 마이크 모드 지원:

````

📱 내 마이크 모드
└── 현재 기기(핸드폰/PC)의 내장 마이크 사용
└── 간편하지만 하울링 주의

🖥️ 서버PC 마이크 모드
└── 서버에 연결된 전문 마이크 선택
└── 고음질 방송 가능
└── 마이크 장치 목록에서 선택

plaintext

```plaintext

### 🌐 신규 채널 동적 추가
관리자 페이지 → [➕ 채널 추가]:

```

채널 키: french
표시 이름: Français
국기: 🇫🇷
LiveKit Room: room\_fr

plaintext

```plaintext
→ 즉시 메인 페이지와 관리자 페이지에 반영

### 💬 카카오톡 스타일 채팅

```

관리자/통역자 ← 금색 말풍선 (왼쪽)
내 메시지 → 노란색 말풍선 (오른쪽, #FEE500)
시스템 알림 ─ 중앙 회색 알약
날짜 구분선 ─ "2026년 6월 14일"

plaintext

````plaintext

---

## 🔧 문제 해결

### iOS에서 "server was not reachable" 오류
```bash
# Nginx 19443 → LiveKit 7880 프록시 확인
curl -sk -H "Upgrade: websocket" \
  -H "Connection: Upgrade" \
  https://서버IP:19443/rtc
# 401 응답이면 정상
```

### 청취자 연결 실패 (ICE connection failed)
```bash
# LiveKit node_ip 확인
docker logs ts_livekit 2>&1 | grep nodeIP
# "nodeIP": "192.168.0.15" ← 실제 LAN IP여야 함

# Docker 내부 IP(172.x.x.x)가 나오면:
/opt/translation-system/scripts/update-ip.sh
```

### UDP 포트 방화벽 오류
```bash
# Ubuntu UFW 설정
sudo ufw allow 55000:55100/udp
sudo ufw allow 17880/tcp
sudo ufw allow 17881/tcp
sudo ufw allow 19000/tcp
sudo ufw allow 19443/tcp
```

### 청취 버튼 클릭 후 소리 안 남
```bash
# 통역자가 방송 중인지 확인
docker logs ts_livekit --tail=5
# "mediaTrack published" 로그 확인

# 브라우저 강력 새로고침
# Windows: Ctrl+Shift+R
# Mac: Cmd+Shift+R
```

### API 서비스 재시작
```bash
cd /opt/translation-system
docker compose restart api
docker compose restart nginx
docker compose restart livekit
```

---

## 📊 모니터링

| 서비스 | URL | 계정 |
|--------|-----|------|
| Grafana | http://서버IP:19300 | admin / 설정값 |
| MinIO | http://서버IP:19011 | minioadmin / 설정값 |
| Prometheus | http://서버IP:9090 | - |

---

## 🗂️ 프로젝트 구조

````

IBS/
├── backend/
│ └── app/
│ ├── main.py # FastAPI 앱 진입점
│ ├── config.py # 환경변수 설정
│ └── routers/
│ ├── websocket\_router.py # WebSocket + 채널 관리
│ ├── livekit\_router.py # LiveKit 토큰 발급
│ ├── broadcasts.py # 방송 세션 관리
│ └── auth.py # JWT 인증
├── frontend/
│ ├── index.html # 메인 (언어 선택)
│ ├── listen.html # 청취자 페이지
│ ├── admin.html # 관리자 페이지
│ ├── login.html # 로그인
│ └── pages/
│ └── interpreter/
│ └── index.html # 통역자 페이지
├── configs/
│ ├── nginx/conf.d/
│ │ ├── 00-main.conf # 메인 HTTP 설정
│ │ └── 19443-https.conf # iOS HTTPS + /rtc 프록시
│ ├── livekit/
│ │ └── livekit.yaml # LiveKit 서버 설정
│ └── ssl/vitna/ # SSL 인증서
├── scripts/
│ └── update-ip.sh # IP 자동 감지 스크립트
├── docker-compose.yml # 전체 스택 정의
└── .env # 환경변수 (gitignore)

plaintext

```plaintext

---

## 🔐 보안 주의사항

1. `.env` 파일은 절대 Git에 올리지 마세요
2. 프로덕션 환경에서는 Let's Encrypt SSL 인증서 사용
3. 관리자 기본 비밀번호(`admin123`) 반드시 변경
4. LiveKit API Secret은 32자 이상 랜덤 문자열 사용
5. 방화벽에서 필요한 포트만 개방

---

## 📝 라이선스

MIT License

---

## 👨‍💻 개발 히스토리

| 날짜 | 주요 변경사항 |
|------|--------------|
| 2026.06.06 | 초기 시스템 구축 (FastAPI + LiveKit + Nginx) |
| 2026.06.13 | iOS 통역자 wss:// 연결 문제 해결 |
| 2026.06.13 | 청취자 버튼 클릭 시에만 오디오 재생 |
| 2026.06.13 | 채널 선택 / 신규 채널 추가 / 마이크 소스 선택 |
| 2026.06.14 | 청취자 연결 실패 (ICE/포트) 해결 |
| 2026.06.14 | 카카오톡 스타일 채팅 UI |
| 2026.06.14 | iOS Safari 청취자 페이지 404 해결 |
| 2026.06.14 | IP 자동 감지 스크립트 |


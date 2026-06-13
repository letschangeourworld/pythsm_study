#!/bin/bash
# ============================================================
# Vitna 다국어 통역방송 시스템 - 최종 배포 스크립트
# 특징:
#   - IP 자동 감지 (랜선 변경해도 자동 적용)
#   - SSL 인증서 IP 변경 시 자동 재생성
#   - DB 스키마 중복 초기화 방지
#   - 모든 수정사항 자동 반영
#
# 사용법:
#   테스트: bash deploy.sh
#   운영:   bash deploy.sh --production
#   업데이트만: bash deploy.sh --skip-build
# ============================================================
set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'
RED='\033[0;31m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

log()  { echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()  { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
step() { echo -e "\n${CYAN}${BOLD}━━━ $1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PRODUCTION=false
SKIP_BUILD=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --production|-p) PRODUCTION=true;  shift ;;
    --skip-build)    SKIP_BUILD=true;  shift ;;
    --help|-h)
      echo "사용법: bash deploy.sh [옵션]"
      echo "  (없음)         테스트 모드 (HTTP + IP)"
      echo "  --production   운영 모드 (HTTPS + 도메인)"
      echo "  --skip-build   API 빌드 건너뜀"
      exit 0 ;;
    *) warn "알 수 없는 옵션: $1"; shift ;;
  esac
done

echo -e "${CYAN}${BOLD}"
echo "  ╔════════════════════════════════════════╗"
echo "  ║   Vitna 통역방송 시스템 배포           ║"
if [ "$PRODUCTION" = true ]; then
echo "  ║   🌐 운영 모드 (HTTPS + 도메인)        ║"
else
echo "  ║   🔧 테스트 모드 (HTTP + IP)           ║"
fi
echo "  ╚════════════════════════════════════════╝"
echo -e "${NC}"

# ── Step 1: .env 로드 및 IP 자동 감지 ─────────────────────
step "환경변수 및 IP 감지"

[ -f .env ] || {
  [ -f .env.example ] && cp .env.example .env || \
    err ".env 파일 없음. .env.example을 복사하여 설정하세요."
  warn ".env 파일을 설정 후 다시 실행하세요: nano .env"
  exit 1
}

source .env

# ★ IP 자동 감지 (랜선 변경 시에도 자동 적용)
CURRENT_IP=$(hostname -I | awk '{print $1}')
log "현재 서버 IP: ${CURRENT_IP}"

if [ -z "${SERVER_IP:-}" ] || [ "${SERVER_IP}" != "${CURRENT_IP}" ]; then
  if [ -n "${SERVER_IP:-}" ] && [ "${SERVER_IP}" != "YOUR_SERVER_IP" ]; then
    warn "IP 변경 감지: ${SERVER_IP} → ${CURRENT_IP}"
    warn "SSL 인증서 및 LiveKit 설정을 새 IP로 재생성합니다."
  fi
  sed -i "s/SERVER_IP=.*/SERVER_IP=${CURRENT_IP}/" .env
  sed -i "s/PUBLIC_IP=.*/PUBLIC_IP=${CURRENT_IP}/" .env
  source .env
fi

log "사용 IP: ${SERVER_IP}"

if [ "$PRODUCTION" = true ]; then
  sed -i 's/TEST_MODE=.*/TEST_MODE=false/' .env
  [ -z "${DOMAIN:-}" ] || [ "${DOMAIN}" = "${SERVER_IP}" ] && \
    err "운영 모드에서는 DOMAIN을 실제 도메인으로 설정하세요. (예: translate.vitna.net)"
else
  sed -i 's/TEST_MODE=.*/TEST_MODE=true/' .env
  DOMAIN="${SERVER_IP}"
fi

source .env
log "DOMAIN: ${DOMAIN:-$SERVER_IP}"

# ── Step 2: LiveKit 설정 (IP 자동 반영) ───────────────────
step "LiveKit 설정"

mkdir -p configs/livekit

cat > configs/livekit/livekit.yaml << EOF
port: 7880
log_level: info

rtc:
  tcp_port: 7881
  port_range_start: 55000
  port_range_end: 55100
  use_external_ip: false
  node_ip: ${SERVER_IP}

redis:
  address: ts_redis:6379
  password: ${REDIS_PASSWORD}

keys:
  ${LIVEKIT_API_KEY}: ${LIVEKIT_API_SECRET}

room:
  auto_create: true
  empty_timeout: 300
  max_participants: 500

turn:
  enabled: false

webhook:
  api_key: ${LIVEKIT_API_KEY}
  urls:
    - http://ts_api:8000/api/v1/webhooks/livekit

logging:
  pion_level: error
EOF

log "LiveKit node_ip: ${SERVER_IP}"

# ── Step 3: coturn 설정 ────────────────────────────────────
mkdir -p configs/coturn

cat > configs/coturn/turnserver.conf << EOF
listening-port=3478
fingerprint
use-auth-secret
static-auth-secret=SecureSecret2026TurnKey32Chars!!
realm=translation.local
total-quota=100
no-loopback-peers
no-multicast-peers
external-ip=${SERVER_IP}
log-file=/var/log/turnserver.log
simple-log
no-cli
no-tls
no-dtls
EOF

log "coturn 설정 완료"

# ── Step 4: SSL 인증서 (IP 변경 시 자동 재생성) ───────────
step "SSL 인증서"

mkdir -p configs/ssl

if [ "$PRODUCTION" = true ]; then
  # 운영: Let's Encrypt
  CERT_PATH="/etc/letsencrypt/live/${DOMAIN}"
  if [ ! -f "${CERT_PATH}/fullchain.pem" ]; then
    log "Let's Encrypt 발급 중: ${DOMAIN}"
    sudo apt install -y certbot 2>/dev/null || true
    docker stop ts_nginx 2>/dev/null || true
    sudo certbot certonly --standalone \
      -d "${DOMAIN}" \
      --email "${SSL_EMAIL:-admin@vitna.net}" \
      --agree-tos --non-interactive --quiet || {
      warn "Let's Encrypt 실패 → 자체 서명 인증서 사용"
      PRODUCTION=false
    }
    sudo systemctl enable certbot.timer 2>/dev/null || true
  fi
  if [ "$PRODUCTION" = true ]; then
    cp "${CERT_PATH}/fullchain.pem" configs/ssl/cert.pem
    cp "${CERT_PATH}/privkey.pem"   configs/ssl/key.pem
    log "Let's Encrypt 인증서 적용"
  fi
fi

# 테스트 모드: IP 기반 자체 서명 인증서
# IP 변경 시 자동 재생성
CERT_IP=""
if [ -f configs/ssl/cert.pem ]; then
  CERT_IP=$(openssl x509 -in configs/ssl/cert.pem -noout -text 2>/dev/null \
    | grep "Subject:" | grep -oP '\d+\.\d+\.\d+\.\d+' | head -1 || echo "")
fi

if [ "$PRODUCTION" = false ]; then
  if [ ! -f configs/ssl/cert.pem ] || [ "${CERT_IP}" != "${SERVER_IP}" ]; then
    if [ -n "${CERT_IP}" ] && [ "${CERT_IP}" != "${SERVER_IP}" ]; then
      warn "SSL 인증서 IP 불일치: ${CERT_IP} → ${SERVER_IP} (재생성)"
    fi
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
      -keyout configs/ssl/key.pem \
      -out    configs/ssl/cert.pem \
      -subj   "/C=KR/ST=Seoul/O=Vitna/CN=${SERVER_IP}" \
      -addext "subjectAltName=IP:${SERVER_IP}" 2>/dev/null
    log "자체 서명 SSL 인증서 생성 (IP: ${SERVER_IP})"
  else
    log "SSL 인증서 유효 (IP: ${CERT_IP})"
  fi
fi

# ── Step 5: Nginx 설정 ────────────────────────────────────
step "Nginx 설정"

mkdir -p configs/nginx/conf.d

cat > configs/nginx/nginx.conf << 'NGINX_EOF'
user  nginx;
worker_processes  auto;
error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;
events { worker_connections 1024; use epoll; multi_accept on; }
http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    types { font/ttf ttf; font/otf otf; }
    log_format main '$remote_addr [$time_local] "$request" $status $body_bytes_sent';
    access_log /var/log/nginx/access.log main;
    error_log  /var/log/nginx/error.log warn;
    sendfile on; tcp_nopush on; tcp_nodelay on; keepalive_timeout 65;
    gzip on;
    gzip_types text/plain application/json application/javascript text/css;
    map $http_upgrade $connection_upgrade {
        default upgrade;
        ''      close;
    }
    include /etc/nginx/conf.d/*.conf;
}
NGINX_EOF

if [ "$PRODUCTION" = true ]; then
  # 운영: HTTP→HTTPS + 단일 도메인
  cat > configs/nginx/conf.d/00-redirect.conf << EOF
server {
    listen 80;
    server_name ${DOMAIN};
    return 301 https://\$host\$request_uri;
}
EOF

  cat > configs/nginx/conf.d/01-main.conf << EOF
server {
    listen 443 ssl http2;
    server_name ${DOMAIN};
    ssl_certificate     /etc/ssl/vitna/cert.pem;
    ssl_certificate_key /etc/ssl/vitna/key.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    add_header Strict-Transport-Security "max-age=63072000" always;
    root /usr/share/nginx/html;
    index index.html;
    location ~* \\.html\$ { add_header Cache-Control "no-store"; expires 0; }
    location ~* \\.(js|css|png|jpg|ttf|woff2|svg|webp)\$ { expires 7d; access_log off; }
    location /fonts/ { try_files \$uri =404; expires 7d; add_header Access-Control-Allow-Origin "*"; }
    location /img/   { try_files \$uri =404; }
    location /css/   { try_files \$uri =404; }
    location /js/    { try_files \$uri =404; }
    location /ws {
        proxy_pass http://ts_api:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_read_timeout 86400s;
    }
    location /api/ {
        proxy_pass http://ts_api:8000/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_http_version 1.1;
        proxy_read_timeout 300;
    }
    location / { try_files \$uri \$uri/ /index.html; }
}
EOF

else
  # 테스트: HTTP 포트 + HTTPS 19443 (iOS 마이크용)
  rm -f configs/nginx/conf.d/*.conf

  for PORT_INFO in "19000:메인포털" "19080:관리자UI" "19081:청취자UI" "19082:통역자UI"; do
    PORT=$(echo $PORT_INFO | cut -d: -f1)
    DESC=$(echo $PORT_INFO | cut -d: -f2)
    cat > configs/nginx/conf.d/${PORT}.conf << EOF
# ${DESC} (HTTP)
server {
    listen ${PORT};
    server_name ${PORT};
    root /usr/share/nginx/html;
    index index.html;
    location ~* \\.html\$ { add_header Cache-Control "no-store"; expires 0; }
    location ~* \\.(js|css|png|jpg|ttf|woff2)\$ { expires 1h; access_log off; }
    location /fonts/ { try_files \$uri =404; expires 7d; add_header Access-Control-Allow-Origin "*"; }
    location /img/   { try_files \$uri =404; }
    location /css/   { try_files \$uri =404; }
    location /js/    { try_files \$uri =404; }
    location /ws {
        proxy_pass         http://ts_api:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header   Upgrade    \$http_upgrade;
        proxy_set_header   Connection "upgrade";
        proxy_set_header   Host       \$host;
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
    location /api/ {
        proxy_pass         http://ts_api:8000/api/;
        proxy_set_header   Host       \$host;
        proxy_set_header   X-Real-IP  \$remote_addr;
        proxy_http_version 1.1;
        proxy_set_header   Upgrade    \$http_upgrade;
        proxy_set_header   Connection \$connection_upgrade;
        proxy_read_timeout 300;
    }
    location / { try_files \$uri \$uri/ /index.html; }
}
EOF
  done

  # 19443: HTTPS (iOS 마이크 허용)
  cat > configs/nginx/conf.d/19443-https.conf << 'EOF'
server {
    listen 19443 ssl;
    server_name _;
    ssl_certificate     /etc/ssl/vitna/cert.pem;
    ssl_certificate_key /etc/ssl/vitna/key.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    root /usr/share/nginx/html;
    index index.html;
    location ~* \.html$ { add_header Cache-Control "no-store"; expires 0; }
    location /fonts/ { try_files $uri =404; expires 7d; add_header Access-Control-Allow-Origin "*"; }
    location /img/   { try_files $uri =404; }
    location /css/   { try_files $uri =404; }
    location /js/    { try_files $uri =404; }
    location /ws {
        proxy_pass         http://ts_api:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header   Upgrade    $http_upgrade;
        proxy_set_header   Connection "upgrade";
        proxy_set_header   Host       $host;
        proxy_read_timeout 86400s;
    }
    location /api/ {
        proxy_pass         http://ts_api:8000/api/;
        proxy_set_header   Host $host;
        proxy_http_version 1.1;
        proxy_read_timeout 300;
    }
    location / { try_files $uri $uri/ /index.html; }
}
EOF

fi

log "Nginx 설정 완료"

# ── Step 6: docker-compose.yml 생성 ───────────────────────
step "Docker Compose 설정"

# 볼륨 마운트: /data 또는 로컬 data/ 디렉토리
DATA_DIR="/data"
if [ ! -d "$DATA_DIR" ] || [ ! -w "$DATA_DIR" ]; then
  DATA_DIR="${SCRIPT_DIR}/data"
  warn "/data 없음 → ${DATA_DIR} 사용"
fi
mkdir -p "${DATA_DIR}"/{postgres,redis,minio,grafana,loki,logs/nginx,logs/api}
mkdir -p "${SCRIPT_DIR}"/{backups/postgres,configs/ssl}

if [ "$PRODUCTION" = true ]; then
  NGINX_PORTS='"80:80"\n      - "443:443"'
else
  NGINX_PORTS='"19000:19000"\n      - "19080:19080"\n      - "19081:19081"\n      - "19082:19082"\n      - "19443:19443"'
fi

cat > docker-compose.yml << COMPOSE_EOF
networks:
  frontend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.30.0.0/24
  backend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.31.0.0/24
  monitoring:
    driver: bridge
    ipam:
      config:
        - subnet: 172.32.0.0/24

services:

  postgres:
    image: pgvector/pgvector:pg17
    container_name: ts_postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: \${POSTGRES_DB}
      POSTGRES_USER: \${POSTGRES_USER}
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD}
      TZ: Asia/Seoul
    ports:
      - "127.0.0.1:15432:5432"
    volumes:
      - ${DATA_DIR}/postgres:/var/lib/postgresql/data
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U \${POSTGRES_USER} -d \${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 10
      start_period: 30s

  redis:
    image: redis:7-alpine
    container_name: ts_redis
    restart: unless-stopped
    command:
      - redis-server
      - --appendonly
      - "yes"
      - --requirepass
      - \${REDIS_PASSWORD}
      - --maxmemory
      - "1gb"
      - --maxmemory-policy
      - "allkeys-lru"
    ports:
      - "127.0.0.1:16379:6379"
    volumes:
      - ${DATA_DIR}/redis:/data
    networks:
      - backend
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "\${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 10

  minio:
    image: minio/minio:latest
    container_name: ts_minio
    restart: unless-stopped
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: \${MINIO_ROOT_USER}
      MINIO_ROOT_PASSWORD: \${MINIO_ROOT_PASSWORD}
      TZ: Asia/Seoul
    ports:
      - "127.0.0.1:19010:9000"
      - "19011:9001"
    volumes:
      - ${DATA_DIR}/minio:/data
    networks:
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 10s
      retries: 5

  livekit:
    image: livekit/livekit-server:latest
    container_name: ts_livekit
    restart: unless-stopped
    command: --config /etc/livekit/livekit.yaml
    environment:
      LIVEKIT_KEYS: "\${LIVEKIT_API_KEY}: \${LIVEKIT_API_SECRET}"
    volumes:
      - ./configs/livekit/livekit.yaml:/etc/livekit/livekit.yaml:ro
    ports:
      - "17880:7880"
      - "17881:7881/tcp"
      - "55000-55100:55000-55100/udp"
    networks:
      - backend
      - frontend
    depends_on:
      redis:
        condition: service_healthy

  coturn:
    image: coturn/coturn:latest
    container_name: ts_coturn
    restart: unless-stopped
    ports:
      - "13478:3478/tcp"
      - "13478:3478/udp"
    volumes:
      - ./configs/coturn/turnserver.conf:/etc/coturn/turnserver.conf:ro
    command: -c /etc/coturn/turnserver.conf
    networks:
      - frontend

  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: ts_api
    restart: unless-stopped
    env_file:
      - .env
    environment:
      DATABASE_URL: "postgresql+asyncpg://\${POSTGRES_USER}:\${POSTGRES_PASSWORD}@ts_postgres:5432/\${POSTGRES_DB}"
      REDIS_URL: "redis://:\${REDIS_PASSWORD}@ts_redis:6379"
      MINIO_ENDPOINT: "ts_minio:9000"
      MINIO_ACCESS_KEY: "\${MINIO_ROOT_USER}"
      MINIO_SECRET_KEY: "\${MINIO_ROOT_PASSWORD}"
      LIVEKIT_URL: "ws://ts_livekit:7880"
      LIVEKIT_API_KEY: "\${LIVEKIT_API_KEY}"
      LIVEKIT_API_SECRET: "\${LIVEKIT_API_SECRET}"
      JWT_SECRET: "\${JWT_SECRET}"
      SERVER_IP: "\${SERVER_IP}"
      PUBLIC_IP: "\${SERVER_IP}"
      LOG_LEVEL: "info"
      PORT_MAIN: "19000"
      PORT_ADMIN: "19080"
      PORT_LISTENER: "19081"
      PORT_INTERPRETER: "19082"
    expose:
      - "8000"
    volumes:
      - ./backend:/app
      - ${DATA_DIR}/logs/api:/app/logs
    networks:
      - backend
      - frontend
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      minio:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/system/health"]
      interval: 15s
      timeout: 10s
      retries: 10
      start_period: 40s

  nginx:
    image: nginx:alpine
    container_name: ts_nginx
    restart: unless-stopped
    ports:
      - "${NGINX_PORTS}"
    volumes:
      - ./configs/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./configs/nginx/conf.d:/etc/nginx/conf.d:ro
      - ./frontend:/usr/share/nginx/html:ro
      - ${DATA_DIR}/logs/nginx:/var/log/nginx
      - ./configs/ssl:/etc/ssl/vitna:ro
    networks:
      - frontend
      - backend
    depends_on:
      - api

  prometheus:
    image: prom/prometheus:latest
    container_name: ts_prometheus
    restart: unless-stopped
    command:
      - --config.file=/etc/prometheus/prometheus.yml
      - --storage.tsdb.path=/prometheus
      - --storage.tsdb.retention.time=30d
      - --web.enable-lifecycle
    ports:
      - "19090:9090"
    volumes:
      - ./configs/prometheus:/etc/prometheus:ro
    networks:
      - monitoring
      - backend

  grafana:
    image: grafana/grafana:latest
    container_name: ts_grafana
    restart: unless-stopped
    environment:
      GF_SECURITY_ADMIN_USER: \${GRAFANA_ADMIN_USER}
      GF_SECURITY_ADMIN_PASSWORD: \${GRAFANA_ADMIN_PASSWORD}
      GF_SERVER_HTTP_PORT: "3000"
      GF_SERVER_ROOT_URL: "http://\${SERVER_IP}:19300"
      TZ: Asia/Seoul
    ports:
      - "19300:3000"
    volumes:
      - ${DATA_DIR}/grafana:/var/lib/grafana
      - ./configs/grafana/provisioning:/etc/grafana/provisioning:ro
    networks:
      - monitoring
    depends_on:
      - prometheus

  loki:
    image: grafana/loki:2.9.0
    container_name: ts_loki
    restart: unless-stopped
    command: -config.file=/etc/loki/config.yaml
    ports:
      - "127.0.0.1:13100:3100"
    volumes:
      - ./configs/loki/config.yaml:/etc/loki/config.yaml:ro
      - ${DATA_DIR}/loki:/loki
    networks:
      - monitoring

  node-exporter:
    image: prom/node-exporter:latest
    container_name: ts_node_exporter
    restart: unless-stopped
    pid: host
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - --path.procfs=/host/proc
      - --path.sysfs=/host/sys
      - --path.rootfs=/rootfs
      - --collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)
    ports:
      - "127.0.0.1:19100:9100"
    networks:
      - monitoring

  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    container_name: ts_postgres_exporter
    restart: unless-stopped
    environment:
      DATA_SOURCE_NAME: "postgresql://\${POSTGRES_USER}:\${POSTGRES_PASSWORD}@ts_postgres:5432/\${POSTGRES_DB}?sslmode=disable"
    ports:
      - "127.0.0.1:19187:9187"
    networks:
      - monitoring
      - backend
    depends_on:
      postgres:
        condition: service_healthy

  redis-exporter:
    image: oliver006/redis_exporter:latest
    container_name: ts_redis_exporter
    restart: unless-stopped
    environment:
      REDIS_ADDR: redis://ts_redis:6379
      REDIS_PASSWORD: \${REDIS_PASSWORD}
    ports:
      - "127.0.0.1:19121:9121"
    networks:
      - monitoring
      - backend
    depends_on:
      redis:
        condition: service_healthy

COMPOSE_EOF

log "docker-compose.yml 생성 완료"

# ── Step 7: 방화벽 ────────────────────────────────────────
step "방화벽 설정"

sudo ufw allow ssh         2>/dev/null || true
sudo ufw allow 19000/tcp   2>/dev/null || true
sudo ufw allow 19080/tcp   2>/dev/null || true
sudo ufw allow 19081/tcp   2>/dev/null || true
sudo ufw allow 19082/tcp   2>/dev/null || true
sudo ufw allow 19443/tcp   2>/dev/null || true
sudo ufw allow 19011/tcp   2>/dev/null || true
sudo ufw allow 19300/tcp   2>/dev/null || true
sudo ufw allow 17880/tcp   2>/dev/null || true
sudo ufw allow 17881/tcp   2>/dev/null || true
sudo ufw allow 55000:55100/udp 2>/dev/null || true
sudo ufw allow from 172.16.0.0/12 2>/dev/null || true

if [ "$PRODUCTION" = true ]; then
  sudo ufw allow 80/tcp    2>/dev/null || true
  sudo ufw allow 443/tcp   2>/dev/null || true
fi

sudo ufw --force enable 2>/dev/null || true
log "방화벽 완료"

# ── Step 8: 서비스 기동 ───────────────────────────────────
step "서비스 기동"

log "인프라 기동..."
docker compose up -d postgres redis minio
log "40초 대기..."
sleep 40

for i in $(seq 1 12); do
  docker exec ts_postgres pg_isready \
    -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" &>/dev/null && break
  sleep 5
done
log "PostgreSQL OK"

# ★ DB 스키마: 없을 때만 초기화 (중복 방지)
TABLE_COUNT=$(docker exec ts_postgres psql -U "${POSTGRES_USER}" \
  -d "${POSTGRES_DB}" -t \
  -c "SELECT COUNT(*) FROM information_schema.tables
      WHERE table_schema='broadcast'" 2>/dev/null | tr -d ' \n' || echo "0")

if [ "${TABLE_COUNT:-0}" -lt "5" ]; then
  log "DB 스키마 초기화 (첫 실행)..."
  for f in 01_extensions 02_schemas 03_auth_tables \
           04_broadcast_tables 05_ai_tables \
           06_audit_tables 07_monitoring_tables; do
    [ -f "sql/${f}.sql" ] && \
      docker exec -i ts_postgres psql \
        -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" \
        < "sql/${f}.sql" 2>&1 | grep -E "^ERROR|^FATAL" || true
    log "  ✓ ${f}.sql"
  done
else
  log "DB 스키마 이미 존재 (${TABLE_COUNT}개 테이블) - 초기화 건너뜀"
fi

log "MinIO 버킷 생성..."
NETWORK=$(docker network ls --format "{{.Name}}" \
  | grep "translation-system" | grep "backend" | head -1 || echo "")

if [ -n "${NETWORK}" ]; then
  docker run --rm --network "${NETWORK}" minio/mc \
    alias set myminio http://ts_minio:9000 \
    "${MINIO_ROOT_USER}" "${MINIO_ROOT_PASSWORD}" 2>/dev/null || true
  for bucket in recordings subtitles translations backup; do
    docker run --rm --network "${NETWORK}" \
      minio/mc mb --ignore-existing "myminio/${bucket}" 2>/dev/null || true
  done
  log "MinIO 버킷 OK"
fi

log "LiveKit + coturn 기동..."
docker compose up -d livekit coturn
sleep 10

log "Backend API 빌드..."
if [ "$SKIP_BUILD" = true ]; then
  docker compose up -d api
else
  docker compose up -d --build api
fi

log "API 응답 대기..."
for i in $(seq 1 36); do
  curl -sf http://localhost:8000/api/v1/system/health &>/dev/null && \
    { log "API OK (${i}회 시도)"; break; }
  printf "."
  sleep 10
done
echo ""

log "Nginx 기동..."
docker compose up -d nginx
sleep 5
docker exec ts_nginx nginx -t 2>&1 | grep -E "ok|error" || true

log "모니터링 기동..."
docker compose up -d prometheus grafana loki \
  node-exporter postgres-exporter redis-exporter 2>/dev/null || true
sleep 5

# ── 완료 ──────────────────────────────────────────────────
echo ""
docker compose ps
echo ""

echo -e "${GREEN}${BOLD}"
echo "╔══════════════════════════════════════════════════════╗"
if [ "$PRODUCTION" = true ]; then
echo "║  🌐 운영 모드 배포 완료!                            ║"
else
echo "║  🔧 테스트 모드 배포 완료!                          ║"
fi
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo "  서버 IP: ${SERVER_IP}"
echo ""

if [ "$PRODUCTION" = true ]; then
  echo "📌 접속 URL (외부 인터넷):"
  echo "  메인:       https://${DOMAIN}"
  echo "  청취자:     https://${DOMAIN}/listen.html?ch=english"
  echo "  통역자:     https://${DOMAIN}/pages/interpreter/index.html"
  echo "  관리자:     https://${DOMAIN}/login.html"
else
  echo "📌 접속 URL (내부망):"
  echo "  메인:       http://${SERVER_IP}:19000"
  echo "  청취자:     http://${SERVER_IP}:19081/listen.html?ch=english"
  echo "  통역자(PC): http://${SERVER_IP}:19082/pages/interpreter/index.html"
  echo "  통역자(iOS): https://${SERVER_IP}:19443/pages/interpreter/index.html"
  echo "              ↑ 경고무시: Safari '고급→이 웹사이트 방문' / Chrome 'thisisunsafe'"
  echo "  관리자:     http://${SERVER_IP}:19000/login.html"
  echo "  Grafana:    http://${SERVER_IP}:19300"
  echo "  MinIO:      http://${SERVER_IP}:19011"
fi

echo ""
echo -e "${YELLOW}  ⚠️  계정: admin / admin123 → 운영 전 반드시 변경!${NC}"


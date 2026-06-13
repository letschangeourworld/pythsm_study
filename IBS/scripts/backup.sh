#!/bin/bash
set -euo pipefail
SCRIPT_DIR="/opt/translation-system"
DATE=$(date +%Y%m%d_%H%M%S)
source "${SCRIPT_DIR}/.env"
mkdir -p "${SCRIPT_DIR}/backups/postgres" "${SCRIPT_DIR}/logs"
LOG="${SCRIPT_DIR}/logs/backup_${DATE}.log"
log(){ echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"|tee -a "$LOG"; }
log "=== 백업 시작 ==="
docker exec postgres pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" \
  --format=custom --compress=9 > "${SCRIPT_DIR}/backups/postgres/db_${DATE}.dump"
log "✅ 완료: db_${DATE}.dump"
find "${SCRIPT_DIR}/backups/postgres" -name "*.dump" -mtime +30 -delete
log "=== 백업 완료 ==="

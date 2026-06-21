#!/bin/bash
echo "=== 헬스체크 $(date) ==="
source /opt/translation-system/.env
cd /opt/translation-system

echo "--- Docker 상태 ---"
docker compose ps

echo "--- API Health ---"
curl -s http://localhost:8000/api/v1/system/health | python3 -m json.tool 2>/dev/null || echo "API 응답 없음"

echo "--- Redis ---"
docker exec redis redis-cli -a "${REDIS_PASSWORD}" ping 2>/dev/null || echo "Redis 응답 없음"

echo "--- MinIO ---"
curl -sf http://localhost:9000/minio/health/live && echo "MinIO: OK" || echo "MinIO: 응답 없음"

echo "--- 리소스 ---"
echo "CPU: $(top -bn1|grep 'Cpu(s)'|awk '{print $2}')%"
echo "RAM: $(free -h|awk 'NR==2{printf "%s/%s",$3,$2}')"
echo "Disk: $(df -h /|awk 'NR==2{print $5}')"

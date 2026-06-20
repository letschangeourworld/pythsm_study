#!/bin/bash
# ============================================================
# Let's Encrypt SSL 인증서 발급 스크립트
# 실행 전 필요사항:
#   1. 도메인 DNS A레코드 → 현재 공인IP 설정 완료
#   2. 공유기 80, 443 포트포워딩 설정 완료
# ============================================================

DOMAIN="translate.vitna.net"
EMAIL="admin@vitna.net"  # 인증서 만료 알림 이메일

echo "🔍 현재 공인 IP 확인..."
PUBLIC_IP=$(curl -s https://api.ipify.org)
echo "   공인 IP: $PUBLIC_IP"

echo ""
echo "🔍 DNS 확인..."
DNS_IP=$(dig +short $DOMAIN 2>/dev/null | tail -1)
echo "   $DOMAIN → $DNS_IP"

if [ "$PUBLIC_IP" != "$DNS_IP" ]; then
    echo "⚠️  DNS가 현재 공인IP와 다릅니다!"
    echo "   도메인 관리 사이트에서 A레코드를 $PUBLIC_IP 로 변경하세요"
    echo "   변경 후 DNS 전파까지 최대 24시간 소요"
    exit 1
fi

echo "✅ DNS 확인 완료"
echo ""

# certbot 설치
echo "📦 certbot 설치 중..."
apt-get update -qq
apt-get install -y certbot

# 80 포트가 열려있는지 확인
echo "🔍 80 포트 확인..."
curl -s --max-time 5 http://$PUBLIC_IP:80 > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️  80 포트가 열려있지 않습니다. 포트포워딩을 확인하세요"
    exit 1
fi

# Nginx 잠시 중지 (80 포트 사용)
echo "🔄 Nginx 잠시 중지..."
cd /opt/translation-system
docker compose stop nginx

# Let's Encrypt 인증서 발급
echo "🔐 SSL 인증서 발급 중..."
certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --email $EMAIL \
    -d $DOMAIN \
    -d www.$DOMAIN 2>/dev/null || \
certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --email $EMAIL \
    -d $DOMAIN

if [ $? -ne 0 ]; then
    echo "❌ 인증서 발급 실패"
    docker compose start nginx
    exit 1
fi

# 인증서를 Nginx 경로로 복사
echo "📋 인증서 복사..."
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem \
   /opt/translation-system/configs/ssl/vitna/cert.pem
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem \
   /opt/translation-system/configs/ssl/vitna/key.pem

echo "✅ 인증서 복사 완료"

# Nginx 재시작
docker compose start nginx
sleep 3
docker exec ts_nginx nginx -t && echo "✅ Nginx 설정 정상"

echo ""
echo "============================================"
echo "✅ SSL 설정 완료!"
echo "   도메인: https://$DOMAIN"
echo "   인증서 만료: $(openssl x509 -enddate -noout \
     -in /opt/translation-system/configs/ssl/vitna/cert.pem \
     | cut -d= -f2)"
echo "============================================"

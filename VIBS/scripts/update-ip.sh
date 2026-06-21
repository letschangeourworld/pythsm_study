#!/bin/bash
echo "🔍 현재 네트워크 IP 감지 중..."

# Docker가 완전히 올라올 때까지 대기
sleep 10

get_lan_ip() {
    # 1순위: 192.168.x.x (일반 가정/사무실 LAN)
    for ip in $(hostname -I 2>/dev/null); do
        if [[ "$ip" =~ ^192\.168\.[0-9]+\.[0-9]+$ ]]; then
            echo "$ip"
            return
        fi
    done
    # 2순위: 10.x.x.x (기업망)
    for ip in $(hostname -I 2>/dev/null); do
        if [[ "$ip" =~ ^10\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            echo "$ip"
            return
        fi
    done
    # 3순위: 172.16~31.x.x (사설망, Docker 제외)
    for ip in $(hostname -I 2>/dev/null); do
        if [[ "$ip" =~ ^172\.(1[6-9]|2[0-9]|30|31)\. ]]; then
            echo "$ip"
            return
        fi
    done
    echo ""
}

NEW_IP=$(get_lan_ip)

if [ -z "$NEW_IP" ]; then
    echo "❌ LAN IP 감지 실패 - 네트워크 연결을 확인하세요"
    exit 1
fi

echo "✅ 감지된 LAN IP: $NEW_IP"
CURRENT_IP=$(grep "^SERVER_IP=" /opt/translation-system/.env | cut -d'=' -f2)
echo "📋 현재 설정 IP: $CURRENT_IP"

# IP가 같으면 불필요한 재시작 생략
if [ "$NEW_IP" == "$CURRENT_IP" ]; then
    echo "✅ IP 변경 없음 ($NEW_IP) - 재시작 생략"
    # livekit.yaml만 확인
    grep "node_ip" /opt/translation-system/configs/livekit/livekit.yaml
    exit 0
fi

echo "🔄 IP 변경 감지: $CURRENT_IP → $NEW_IP"

# .env 업데이트
sed -i "s/SERVER_IP=.*/SERVER_IP=$NEW_IP/"     /opt/translation-system/.env
sed -i "s/DOMAIN=.*/DOMAIN=$NEW_IP/"            /opt/translation-system/.env
sed -i "s/PUBLIC_IP=.*/PUBLIC_IP=$NEW_IP/"      /opt/translation-system/.env
sed -i "s/SUBDOMAIN=.*/SUBDOMAIN=$NEW_IP/"      /opt/translation-system/.env
sed -i "s/BASE_DOMAIN=.*/BASE_DOMAIN=$NEW_IP/"  /opt/translation-system/.env
echo "✅ .env 업데이트 완료"

# livekit.yaml node_ip 업데이트
sed -i "s/node_ip:.*/node_ip: $NEW_IP/" \
    /opt/translation-system/configs/livekit/livekit.yaml
echo "✅ livekit.yaml node_ip → $NEW_IP"

# 서비스 재시작
echo "🔄 서비스 재시작 중..."
cd /opt/translation-system
docker compose restart livekit api nginx
sleep 8

# LiveKit nodeIP 확인
NODE_IP=$(docker logs ts_livekit 2>&1 | grep "nodeIP" | tail -1 | \
          grep -o '"nodeIP":"[^"]*"' | cut -d'"' -f4)

echo ""
echo "============================================"
echo "✅ IP 업데이트 완료!"
echo "   서버 IP:        $NEW_IP"
echo "   LiveKit nodeIP: $NODE_IP"
echo ""
echo "📱 접속 주소:"
echo "   메인:    http://$NEW_IP:19000"
echo "   관리자:  http://$NEW_IP:19000/admin.html"
echo "   청취자:  http://$NEW_IP:19000/listen.html?ch=english"
echo "   통역자:  https://$NEW_IP:19443/pages/interpreter/index.html"
echo "============================================"

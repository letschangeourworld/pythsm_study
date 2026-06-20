#!/bin/bash
echo "🔍 현재 네트워크 IP 감지 중..."

get_lan_ip() {
    # 192.168.x.x 또는 10.x.x.x 대역 우선
    for ip in $(hostname -I 2>/dev/null); do
        if [[ "$ip" =~ ^192\.168\. ]] || [[ "$ip" =~ ^10\. ]]; then
            echo "$ip"
            return
        fi
    done
    # 없으면 172.x.x.x 중 Docker 아닌 것
    for ip in $(hostname -I 2>/dev/null); do
        if [[ "$ip" =~ ^172\. ]] && [[ "$ip" != "172.17."* ]] && \
           [[ "$ip" != "172.18."* ]] && [[ "$ip" != "172.19."* ]] && \
           [[ "$ip" != "172.30."* ]] && [[ "$ip" != "172.31."* ]] && \
           [[ "$ip" != "172.32."* ]]; then
            echo "$ip"
            return
        fi
    done
    hostname -I | awk '{print $1}'
}

NEW_IP=$(get_lan_ip)
if [ -z "$NEW_IP" ]; then
    echo "❌ IP 감지 실패"
    exit 1
fi

echo "✅ 감지된 LAN IP: $NEW_IP"
CURRENT_IP=$(grep "^SERVER_IP=" /opt/translation-system/.env | cut -d'=' -f2)
echo "📋 현재 설정 IP: $CURRENT_IP"

# .env 업데이트
sed -i "s/SERVER_IP=.*/SERVER_IP=$NEW_IP/" /opt/translation-system/.env
sed -i "s/DOMAIN=.*/DOMAIN=$NEW_IP/"       /opt/translation-system/.env
sed -i "s/PUBLIC_IP=.*/PUBLIC_IP=$NEW_IP/" /opt/translation-system/.env
sed -i "s/SUBDOMAIN=.*/SUBDOMAIN=$NEW_IP/" /opt/translation-system/.env
sed -i "s/BASE_DOMAIN=.*/BASE_DOMAIN=$NEW_IP/" /opt/translation-system/.env
echo "✅ .env 업데이트 완료"

# livekit.yaml node_ip 업데이트 (핵심!)
sed -i "s/node_ip:.*/node_ip: $NEW_IP/" \
    /opt/translation-system/configs/livekit/livekit.yaml
echo "✅ livekit.yaml node_ip → $NEW_IP"

# 서비스 재시작
echo "🔄 서비스 재시작 중..."
cd /opt/translation-system
docker compose restart livekit api nginx
sleep 8

# LiveKit 확인
NODE_IP=$(docker logs ts_livekit 2>&1 | grep "nodeIP" | tail -1 | \
          grep -o '"nodeIP":"[^"]*"' | cut -d'"' -f4)
echo ""
echo "============================================"
echo "✅ IP 업데이트 완료!"
echo "   서버 IP:       $NEW_IP"
echo "   LiveKit nodeIP: $NODE_IP"
echo ""
echo "📱 접속 주소:"
echo "   메인:     http://$NEW_IP:19000"
echo "   관리자:   http://$NEW_IP:19000/admin.html"
echo "   청취자:   http://$NEW_IP:19000/listen.html?ch=english"
echo "   통역자:   https://$NEW_IP:19443/pages/interpreter/index.html"
echo "============================================"

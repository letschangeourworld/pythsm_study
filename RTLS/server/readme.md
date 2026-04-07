Server OS : ubuntu 24.04 LTS
docker container
nginx, FastAPI, Postgresql, Redpanda

FastAPI + Redpanda 실시간 처리 코드 👉 UWB 태그 데이터 스트리밍
WebSocket UI 👉 공장 지도 + 실시간 위치 표시
Kafka Topic 설계 : tag-location + anomaly-detection
Redis 추가 👉 WebSocket 성능 개선
DB 저장 👉 PostgreSQL에 위치 로그 이력 저장
공장 도면 이미지 위에 정확히 좌표 매핑
50~100 Tag 분산 처리 서버 구조 : 멀티 Consumer
AI 기반 이상 탐지 : LSTM / Isolation Forest

구축 순서
1단계 → Docker Compose 전체 구성
2단계 → Redpanda Topic 설계
3단계 → FastAPI + Kafka Producer/Consumer
4단계 → Redis WebSocket 브로드캐스트
5단계 → PostgreSQL 스키마 + 저장
6단계 → AI 이상 탐지 Worker
7단계 → WebSocket UI (공장 지도)

Docker Compose - all services : docker-compose.yml
Nginx config : nginx.conf
PostgreSQL init SQL - schema : init.sql
FastAPI : Dockerfile
DockerfileFastAPI requirements : requirements.txt
FastAPI core config : config.py
Pydantic models for location data : events.py
Redis WebSocket manager - pub/sub broadcast : ws_manager.py
Kafka producer service : kafka_producer.py
Location consumer worker - multi-instance : location_consumer.py
FastAPI main app + WebSocket endpoint : main.py
AI anomaly detection worker - LSTM + Isolation Forest : anomaly_worker.py
AI worker Dockerfile and requirements : Dockerfile
AI worker requirements : requirements.txt

현재 서버 운영체제는 ubuntu 24.04 LTS 인데, 
nginx, FastAPI, Postgresql, Redpanda를 
docker container에 깔고 다음 서비스 처리

FastAPI + Redpanda 실시간 처리 코드 👉 UWB 태그 데이터 스트리밍
WebSocket UI 👉 공장 지도 + 실시간 위치 표시
Kafka Topic 설계 : tag-location + anomaly-detection
Redis 추가 👉 WebSocket 성능 개선
DB 저장 👉 PostgreSQL에 위치 로그 이력 저장
공장 도면 이미지 위에 정확히 좌표 매핑
50~100 Tag 분산 처리 서버 구조 : 멀티 Consumer
AI 기반 이상 탐지 : LSTM / Isolation Forest
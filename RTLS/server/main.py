"""
FastAPI 메인 앱
- REST API: UWB 데이터 수신, 이력 조회
- WebSocket: 실시간 위치 스트리밍
"""
import asyncio
import json
import logging
from contextlib import asynccontextmanager
 
import redis.asyncio as aioredis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
 
from app.core.config import settings
from app.models.events import TagLocationEvent
from app.services.kafka_producer import get_producer, stop_producer, produce_location
from app.services.ws_manager import (
    manager, pubsub_relay, get_all_latest_locations
)
 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
_redis_client: aioredis.Redis | None = None
 
 
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _redis_client
    # 시작
    _redis_client = await aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    await get_producer()
    await pubsub_relay.start()
    logger.info("Application startup complete")
    yield
    # 종료
    await pubsub_relay.stop()
    await stop_producer()
    if _redis_client:
        await _redis_client.close()
 
 
app = FastAPI(title="UWB 실시간 위치 추적 시스템", lifespan=lifespan)
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
 
 
# ─── REST API ─────────────────────────────────────────────
 
@app.post("/api/location", summary="UWB 태그 위치 데이터 수신")
async def ingest_location(event: TagLocationEvent):
    """Location Engine에서 주기적으로 호출 (또는 WebSocket으로도 수신 가능)"""
    await produce_location(event)
    return {"status": "ok", "tag_id": event.tag_id}
 
 
@app.post("/api/location/batch", summary="위치 데이터 배치 수신")
async def ingest_location_batch(events: list[TagLocationEvent]):
    """50~100개 태그의 데이터를 한 번에 수신"""
    for event in events:
        await produce_location(event)
    return {"status": "ok", "count": len(events)}
 
 
@app.get("/api/tags/locations", summary="전체 태그 최신 위치 조회")
async def get_all_locations():
    """신규 클라이언트 접속 시 현재 상태 초기 로드"""
    locations = await get_all_latest_locations(_redis_client)
    return {"locations": locations, "count": len(locations)}
 
 
@app.get("/api/tags/{tag_id}/history", summary="태그 위치 이력 (Redis 캐시)")
async def get_tag_history(tag_id: str, limit: int = 100):
    key = f"uwb:history:{tag_id}"
    raw = await _redis_client.lrange(key, -limit, -1)
    return {"tag_id": tag_id, "history": [json.loads(r) for r in raw]}
 
 
@app.get("/api/anomalies", summary="미해결 이상 탐지 이벤트 목록")
async def get_anomalies():
    # 실제 구현시 DB 조회, 여기서는 Redis 캐시에서
    keys = await _redis_client.keys("uwb:anomaly:*")
    results = []
    for k in keys:
        v = await _redis_client.get(k)
        if v:
            results.append(json.loads(v))
    return {"anomalies": results}
 
 
# ─── WebSocket ────────────────────────────────────────────
 
@app.websocket("/ws/floor/{floor_id}")
async def websocket_floor(websocket: WebSocket, floor_id: str):
    """
    층별 실시간 위치 스트림
    - 클라이언트 접속 시 현재 전체 태그 위치 초기 전송
    - Redis Pub/Sub 통해 업데이트 수신 → 브로드캐스트
    """
    await manager.connect(websocket, floor_id)
    try:
        # 초기 상태 전송
        locations = await get_all_latest_locations(_redis_client)
        await websocket.send_json({
            "type": "init",
            "floor": floor_id,
            "payload": locations,
        })
 
        # 클라이언트 메시지 수신 루프 (heartbeat / 명령)
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=settings.WS_HEARTBEAT_INTERVAL)
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except asyncio.TimeoutError:
                # heartbeat
                await websocket.send_json({"type": "heartbeat"})
            except WebSocketDisconnect:
                break
    finally:
        manager.disconnect(websocket, floor_id)
        logger.info(f"WS disconnected: floor={floor_id}")
 
 
@app.get("/health")
async def health():
    return {"status": "ok", "ws_connections": manager.count}
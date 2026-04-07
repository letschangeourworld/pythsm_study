"""
Redis Pub/Sub 기반 WebSocket 매니저
- FastAPI 인스턴스 여러 개라도 모든 클라이언트에 브로드캐스트 가능
- Redis channel: uwb:broadcast
"""
import asyncio
import json
import logging
from typing import Dict, Set
from datetime import datetime
 
import redis.asyncio as aioredis
from fastapi import WebSocket
 
from app.core.config import settings
 
logger = logging.getLogger(__name__)
 
REDIS_CHANNEL = "uwb:broadcast"
REDIS_LOC_KEY = "uwb:latest:{tag_id}"   # 태그별 최신 위치 캐시
REDIS_HIST_KEY = "uwb:history:{tag_id}" # 태그별 최근 100개 링 버퍼
 
 
class ConnectionManager:
    """로컬 WebSocket 연결 관리"""
 
    def __init__(self):
        # floor별 구독자 관리
        self._connections: Dict[str, Set[WebSocket]] = {}  # floor_id → set of ws
 
    async def connect(self, websocket: WebSocket, floor_id: str = "1"):
        await websocket.accept()
        self._connections.setdefault(floor_id, set()).add(websocket)
        logger.info(f"WS connected: floor={floor_id}, total={self.count}")
 
    def disconnect(self, websocket: WebSocket, floor_id: str = "1"):
        self._connections.get(floor_id, set()).discard(websocket)
 
    @property
    def count(self) -> int:
        return sum(len(v) for v in self._connections.values())
 
    async def broadcast_to_floor(self, floor_id: str, message: str):
        dead: list = []
        for ws in self._connections.get(floor_id, set()):
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._connections.get(floor_id, set()).discard(ws)
 
    async def broadcast_all(self, message: str):
        for floor_id in list(self._connections.keys()):
            await self.broadcast_to_floor(floor_id, message)
 
 
manager = ConnectionManager()
 
 
class RedisPubSubRelay:
    """
    Redis Pub/Sub → WebSocket 릴레이
    Kafka Consumer가 Redis에 publish → 모든 WS 클라이언트로 전달
    """
 
    def __init__(self):
        self._redis: aioredis.Redis | None = None
        self._pubsub = None
        self._running = False
 
    async def start(self):
        self._redis = await aioredis.from_url(
            settings.REDIS_URL, decode_responses=True
        )
        self._pubsub = self._redis.pubsub()
        await self._pubsub.subscribe(REDIS_CHANNEL)
        self._running = True
        asyncio.create_task(self._relay_loop())
        logger.info("Redis PubSub relay started")
 
    async def stop(self):
        self._running = False
        if self._pubsub:
            await self._pubsub.unsubscribe()
 
    async def _relay_loop(self):
        async for message in self._pubsub.listen():
            if not self._running:
                break
            if message["type"] != "message":
                continue
            data: str = message["data"]
            try:
                parsed = json.loads(data)
                floor_id = str(parsed.get("floor", "1"))
                await manager.broadcast_to_floor(floor_id, data)
                # 전 층 이벤트는 전체 브로드캐스트
                if parsed.get("type") in ("anomaly", "zone_alert"):
                    await manager.broadcast_all(data)
            except Exception as e:
                logger.error(f"Relay error: {e}")
 
    async def publish(self, payload: dict):
        if self._redis:
            await self._redis.publish(REDIS_CHANNEL, json.dumps(payload, default=str))
 
 
pubsub_relay = RedisPubSubRelay()
 
 
async def cache_latest_location(redis: aioredis.Redis, tag_id: str, data: dict):
    """태그 최신 위치를 Redis에 캐시 (TTL 60초)"""
    key = REDIS_LOC_KEY.format(tag_id=tag_id)
    await redis.set(key, json.dumps(data, default=str), ex=60)
 
    # 링 버퍼에 이력 추가 (최근 100개)
    hist_key = REDIS_HIST_KEY.format(tag_id=tag_id)
    pipe = redis.pipeline()
    pipe.rpush(hist_key, json.dumps(data, default=str))
    pipe.ltrim(hist_key, -settings.LOCATION_BUFFER_SIZE, -1)
    pipe.expire(hist_key, 3600)
    await pipe.execute()
 
 
async def get_all_latest_locations(redis: aioredis.Redis) -> list[dict]:
    """전체 태그 최신 위치 일괄 조회 (신규 클라이언트 초기 로드용)"""
    pattern = REDIS_LOC_KEY.format(tag_id="*")
    keys = await redis.keys(pattern)
    if not keys:
        return []
    values = await redis.mget(keys)
    result = []
    for v in values:
        if v:
            try:
                result.append(json.loads(v))
            except Exception:
                pass
    return result

"""
Location Consumer Worker
- tag-location 토픽 소비
- PostgreSQL 위치 로그 저장
- Redis 캐시 갱신
- Redis Pub/Sub publish → WebSocket 브로드캐스트
- 3개 인스턴스 병렬 실행 (docker compose deploy.replicas: 3)
"""
import asyncio
import json
import logging
import os
import signal
from datetime import datetime
 
import redis.asyncio as aioredis
from aiokafka import AIOKafkaConsumer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
 
from app.core.config import settings
from app.services.ws_manager import cache_latest_location, REDIS_CHANNEL
 
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
 
# DB 배치 인서트 크기
BATCH_SIZE = 50
BATCH_TIMEOUT = 2.0  # seconds
 
 
class LocationConsumer:
    def __init__(self):
        self.engine = create_async_engine(settings.DATABASE_URL, pool_size=5)
        self.SessionLocal = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        self.redis: aioredis.Redis | None = None
        self.consumer: AIOKafkaConsumer | None = None
        self._running = False
        self._batch: list = []
        self._batch_lock = asyncio.Lock()
 
    async def start(self):
        self.redis = await aioredis.from_url(settings.REDIS_URL, decode_responses=True)
 
        self.consumer = AIOKafkaConsumer(
            settings.KAFKA_TOPIC_LOCATION,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP,
            group_id=os.getenv("CONSUMER_GROUP", "location-group"),
            auto_offset_reset="latest",
            enable_auto_commit=True,
            max_poll_records=200,
            fetch_max_bytes=10 * 1024 * 1024,  # 10MB
            value_deserializer=lambda v: json.loads(v.decode()),
        )
        await self.consumer.start()
        self._running = True
        logger.info(f"Consumer started | group={os.getenv('CONSUMER_GROUP', 'location-group')}")
 
        # 배치 플러시 태스크 병렬 실행
        await asyncio.gather(
            self._consume_loop(),
            self._batch_flush_loop(),
        )
 
    async def stop(self):
        self._running = False
        if self.consumer:
            await self.consumer.stop()
        await self._flush_batch()
 
    async def _consume_loop(self):
        async for msg in self.consumer:
            if not self._running:
                break
            try:
                await self._handle_message(msg.value)
            except Exception as e:
                logger.error(f"Message handling error: {e}", exc_info=True)
 
    async def _handle_message(self, data: dict):
        tag_id = data.get("tag_id", "unknown")
        ts = data.get("ts", datetime.utcnow().isoformat())
 
        # 1. Redis 최신 위치 캐시 갱신
        await cache_latest_location(self.redis, tag_id, data)
 
        # 2. WebSocket 브로드캐스트 (Redis Pub/Sub)
        ws_payload = {
            "type": "location",
            "floor": data.get("floor", 1),
            "payload": data,
            "ts": ts,
        }
        await self.redis.publish(REDIS_CHANNEL, json.dumps(ws_payload, default=str))
 
        # 3. DB 배치 버퍼에 추가
        async with self._batch_lock:
            self._batch.append(data)
            if len(self._batch) >= BATCH_SIZE:
                await self._flush_batch_locked()
 
    async def _batch_flush_loop(self):
        """주기적 배치 플러시 (최대 2초 지연)"""
        while self._running:
            await asyncio.sleep(BATCH_TIMEOUT)
            await self._flush_batch()
 
    async def _flush_batch(self):
        async with self._batch_lock:
            await self._flush_batch_locked()
 
    async def _flush_batch_locked(self):
        if not self._batch:
            return
        batch = self._batch.copy()
        self._batch.clear()
 
        try:
            async with self.SessionLocal() as session:
                await session.execute(
                    text("""
                        INSERT INTO location_logs (tag_id, x, y, z, zone_id, floor, ts, raw_data)
                        VALUES (:tag_id, :x, :y, :z, :zone_id, :floor, :ts, :raw_data::jsonb)
                    """),
                    [
                        {
                            "tag_id": d.get("tag_id"),
                            "x": d.get("x", 0),
                            "y": d.get("y", 0),
                            "z": d.get("z", 0),
                            "zone_id": d.get("zone_id"),
                            "floor": d.get("floor", 1),
                            "ts": d.get("ts", datetime.utcnow().isoformat()),
                            "raw_data": json.dumps(d.get("raw_data") or {}),
                        }
                        for d in batch
                    ],
                )
                await session.commit()
            logger.debug(f"Flushed {len(batch)} location records to DB")
        except Exception as e:
            logger.error(f"DB flush error: {e}", exc_info=True)
 
 
async def main():
    consumer = LocationConsumer()
 
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(consumer.stop()))
 
    await consumer.start()
 
 
if __name__ == "__main__":
    asyncio.run(main())
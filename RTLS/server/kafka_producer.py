"""
Kafka (Redpanda) Producer
UWB 데이터 수신 → tag-location 토픽으로 전송
"""
import json
import logging
from contextlib import asynccontextmanager
 
from aiokafka import AIOKafkaProducer
from app.core.config import settings
from app.models.events import TagLocationEvent
 
logger = logging.getLogger(__name__)
 
_producer: AIOKafkaProducer | None = None
 
 
async def get_producer() -> AIOKafkaProducer:
    global _producer
    if _producer is None:
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP,
            value_serializer=lambda v: json.dumps(v, default=str).encode(),
            compression_type="lz4",
            max_batch_size=32768,
            linger_ms=5,           # 5ms 배치 수집 (처리량 향상)
            acks="all",
        )
        await _producer.start()
        logger.info("Kafka producer started")
    return _producer
 
 
async def stop_producer():
    global _producer
    if _producer:
        await _producer.stop()
        _producer = None
 
 
async def produce_location(event: TagLocationEvent):
    """태그 위치 이벤트를 Kafka tag-location 토픽으로 발행"""
    producer = await get_producer()
    await producer.send(
        topic=settings.KAFKA_TOPIC_LOCATION,
        key=event.to_kafka_key(),    # tag_id 기반 파티션 → 순서 보장
        value=event.model_dump(),
    )
 
 
async def produce_anomaly(event: dict):
    """이상 탐지 결과를 anomaly-detection 토픽으로 발행"""
    producer = await get_producer()
    await producer.send(
        topic=settings.KAFKA_TOPIC_ANOMALY,
        key=event.get("tag_id", "unknown").encode(),
        value=event,
    )
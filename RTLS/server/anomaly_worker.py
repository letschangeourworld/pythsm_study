"""
AI Anomaly Detection Worker
- Kafka tag-location : topic consumption
- Isolation Forest: immediately anomaly detection (real time)
- LSTM Autoencoder: Timeseries Pattern Anomaly Detection (based on WINDOW)
- In case of anomaly detection, anomaly-detection topic publish + Redis save
"""
import asyncio
import json
import logging
import os
import signal
from collections import defaultdict, deque
from datetime import datetime
 
import numpy as np
import redis.asyncio as aioredis
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
 
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
 
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "redpanda:9092")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "ai-anomaly-group")
 
# LSTM 윈도우 크기 (최근 N개 위치 시퀀스)
LSTM_WINDOW = 20
# Isolation Forest 이상 점수 임계값
IF_THRESHOLD = 0.65
# 최소 속도 기준 (m/s) - 지게차 최대 속도 기준
MAX_SPEED = 5.0
 
 
class IsolationForestDetector:
    """
    Isolation Forest 기반 실시간 이상 탐지
    scikit-learn 의존성 없이 간소화된 구현 (프로덕션에서는 sklearn 사용 권장)
    """
 
    def __init__(self, n_estimators=50, contamination=0.05):
        self.n_estimators = n_estimators
        self.contamination = contamination
        self._fitted = False
        self._training_data: list = []
        self._min_train_samples = 200
 
    def partial_fit(self, features: list[float]):
        self._training_data.append(features)
        if len(self._training_data) >= self._min_train_samples:
            self._fitted = True
 
    def score(self, features: list[float]) -> float:
        """이상 점수 반환 (0~1, 높을수록 이상)"""
        if not self._fitted or len(self._training_data) < 50:
            return 0.0
 
        # 간소화: 마할라노비스 거리 기반 점수 계산
        data = np.array(self._training_data[-500:])  # 최근 500개만
        mean = np.mean(data, axis=0)
        std = np.std(data, axis=0) + 1e-8
 
        z_scores = np.abs((np.array(features) - mean) / std)
        anomaly_score = float(np.mean(z_scores) / (np.mean(z_scores) + 1))
        return min(anomaly_score, 1.0)
 
 
class LSTMWindowDetector:
    """
    LSTM Autoencoder 기반 시계열 이상 탐지
    실제 프로덕션에서는 PyTorch/TensorFlow 모델 로드
    여기서는 재구성 오류 기반 간소화 구현
    """
 
    def __init__(self, window_size: int = LSTM_WINDOW):
        self.window_size = window_size
        self._windows: dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
 
    def add_point(self, tag_id: str, x: float, y: float) -> float:
        """
        윈도우에 포인트 추가 후 이상 점수 반환
        실제 구현: model.predict(window) → reconstruction_error
        """
        window = self._windows[tag_id]
        window.append((x, y))
 
        if len(window) < self.window_size:
            return 0.0
 
        points = np.array(window)
 
        # 선형 회귀 기반 예측 오류 (간소화된 시계열 이상 탐지)
        t = np.arange(len(points))
        try:
            # X 방향 회귀
            cx = np.polyfit(t, points[:, 0], 1)
            cy = np.polyfit(t, points[:, 1], 1)
 
            pred_x = np.polyval(cx, t)
            pred_y = np.polyval(cy, t)
 
            residuals = np.sqrt(
                (points[:, 0] - pred_x) ** 2 + (points[:, 1] - pred_y) ** 2
            )
            mean_res = float(np.mean(residuals[-5:]))  # 최근 5포인트 오류
            # 정규화 (기준: 5m 이상 오류를 1.0으로)
            return min(mean_res / 5.0, 1.0)
        except Exception:
            return 0.0
 
 
class SpeedChecker:
    """태그별 속도 계산 → 비정상 속도 탐지"""
 
    def __init__(self):
        self._last: dict[str, dict] = {}
 
    def check(self, tag_id: str, x: float, y: float, ts: str) -> tuple[float, bool]:
        """(speed_m_s, is_anomaly) 반환"""
        if tag_id not in self._last:
            self._last[tag_id] = {"x": x, "y": y, "ts": ts}
            return 0.0, False
 
        last = self._last[tag_id]
        try:
            t1 = datetime.fromisoformat(last["ts"].replace("Z", "+00:00"))
            t2 = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            dt = (t2 - t1).total_seconds()
            if dt <= 0:
                return 0.0, False
 
            dist = ((x - last["x"]) ** 2 + (y - last["y"]) ** 2) ** 0.5
            speed = dist / dt
        except Exception:
            speed = 0.0
        finally:
            self._last[tag_id] = {"x": x, "y": y, "ts": ts}
 
        return speed, speed > MAX_SPEED
 
 
class AnomalyWorker:
    def __init__(self):
        self.consumer: AIOKafkaConsumer | None = None
        self.producer: AIOKafkaProducer | None = None
        self.redis: aioredis.Redis | None = None
        self._running = False
 
        # 탐지기 초기화
        self.if_detectors: dict[str, IsolationForestDetector] = defaultdict(IsolationForestDetector)
        self.lstm_detector = LSTMWindowDetector()
        self.speed_checker = SpeedChecker()
 
    async def start(self):
        self.redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
 
        self.consumer = AIOKafkaConsumer(
            "tag-location",
            bootstrap_servers=KAFKA_BOOTSTRAP,
            group_id=CONSUMER_GROUP,
            auto_offset_reset="latest",
            value_deserializer=lambda v: json.loads(v.decode()),
        )
        self.producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP,
            value_serializer=lambda v: json.dumps(v, default=str).encode(),
        )
 
        await self.consumer.start()
        await self.producer.start()
        self._running = True
        logger.info("AI Anomaly Worker started")
 
        async for msg in self.consumer:
            if not self._running:
                break
            try:
                await self._process(msg.value)
            except Exception as e:
                logger.error(f"Process error: {e}", exc_info=True)
 
    async def stop(self):
        self._running = False
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()
 
    async def _process(self, data: dict):
        tag_id = data.get("tag_id", "unknown")
        x = float(data.get("x", 0))
        y = float(data.get("y", 0))
        ts = data.get("ts", datetime.utcnow().isoformat())
 
        features = [x, y, data.get("z", 0)]
 
        # 1. Isolation Forest 학습 및 탐지
        if_det = self.if_detectors[tag_id]
        if_det.partial_fit(features)
        if_score = if_det.score(features)
 
        # 2. LSTM 시계열 탐지
        lstm_score = self.lstm_detector.add_point(tag_id, x, y)
 
        # 3. 속도 기반 탐지
        speed, speed_anomaly = self.speed_checker.check(tag_id, x, y, ts)
 
        anomalies_detected = []
 
        if if_score > IF_THRESHOLD:
            anomalies_detected.append({
                "event_type": "isolation_forest",
                "score": round(if_score, 3),
                "description": f"Isolation Forest 이상 감지 (score={if_score:.3f})",
            })
 
        if lstm_score > 0.6:
            anomalies_detected.append({
                "event_type": "lstm_anomaly",
                "score": round(lstm_score, 3),
                "description": f"LSTM 시계열 이상 감지 (score={lstm_score:.3f})",
            })
 
        if speed_anomaly:
            anomalies_detected.append({
                "event_type": "speed_violation",
                "score": min(speed / MAX_SPEED, 1.0),
                "description": f"속도 초과: {speed:.1f} m/s (최대 {MAX_SPEED} m/s)",
            })
 
        for anomaly in anomalies_detected:
            event = {
                "tag_id": tag_id,
                "location": {"x": x, "y": y, "zone_id": data.get("zone_id")},
                "ts": ts,
                **anomaly,
            }
 
            # Kafka anomaly-detection 토픽으로 발행
            await self.producer.send(
                topic="anomaly-detection",
                key=tag_id.encode(),
                value=event,
            )
 
            # Redis 임시 저장 (대시보드 조회용, TTL 1시간)
            await self.redis.set(
                f"uwb:anomaly:{tag_id}:{anomaly['event_type']}",
                json.dumps(event, default=str),
                ex=3600,
            )
 
            # WebSocket 브로드캐스트 (Redis Pub/Sub)
            ws_payload = {
                "type": "anomaly",
                "floor": data.get("floor", 1),
                "payload": event,
            }
            await self.redis.publish("uwb:broadcast", json.dumps(ws_payload, default=str))
 
            logger.warning(f"ANOMALY | tag={tag_id} type={anomaly['event_type']} score={anomaly['score']}")
 
 
async def main():
    worker = AnomalyWorker()
 
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(worker.stop()))
 
    await worker.start()
 
 
if __name__ == "__main__":
    asyncio.run(main())

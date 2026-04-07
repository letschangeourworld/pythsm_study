from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
 
 
class TagLocationEvent(BaseModel):
    """UWB 태그 위치 이벤트 - Kafka 메시지 스키마"""
    tag_id: str
    x: float = Field(..., description="미터 단위 X 좌표")
    y: float = Field(..., description="미터 단위 Y 좌표")
    z: float = Field(0.0, description="미터 단위 Z 좌표 (층)")
    zone_id: Optional[str] = None
    floor: int = 1
    ts: datetime = Field(default_factory=datetime.utcnow)
    raw_data: Optional[dict] = None
 
    def to_kafka_key(self) -> bytes:
        """파티션 키 - tag_id 기반으로 같은 태그는 동일 파티션"""
        return self.tag_id.encode()
 
 
class AnomalyEvent(BaseModel):
    """이상 탐지 이벤트"""
    tag_id: str
    event_type: str   # out_of_zone | speed_violation | isolation_forest | lstm_anomaly
    score: float      # 0.0 ~ 1.0
    description: str
    location: dict    # {x, y, zone_id}
    ts: datetime = Field(default_factory=datetime.utcnow)
 
 
class WSMessage(BaseModel):
    """WebSocket 브로드캐스트 메시지"""
    type: str         # location | anomaly | zone_alert
    payload: Any
    ts: datetime = Field(default_factory=datetime.utcnow)
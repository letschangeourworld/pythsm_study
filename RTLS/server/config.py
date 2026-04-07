from pydantic_settings import BaseSettings
 
class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://uwb:uwbpass@postgres:5432/uwbdb"
    REDIS_URL: str = "redis://redis:6379"
    KAFKA_BOOTSTRAP: str = "redpanda:9092"
    SECRET_KEY: str = "change-me"
    
    KAFKA_TOPIC_LOCATION: str = "tag-location"
    KAFKA_TOPIC_ANOMALY: str = "anomaly-detection"
    KAFKA_TOPIC_EVENTS: str = "location-events"
    
    WS_HEARTBEAT_INTERVAL: int = 30   # seconds
    LOCATION_BUFFER_SIZE: int = 100   # Redis ring buffer per tag
 
    class Config:
        env_file = ".env"
 
settings = Settings()
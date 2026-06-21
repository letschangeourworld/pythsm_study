from functools import lru_cache
from pydantic_settings import BaseSettings
import socket
import os
from urllib.parse import quote

def get_server_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

class Settings(BaseSettings):
    APP_NAME: str = "Translation Broadcasting System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "info"

    SERVER_IP: str = ""
    DOMAIN: str = "localhost"

    # DB 개별 변수 (URL은 property로 조합)
    POSTGRES_DB: str = "vitna"
    POSTGRES_USER: str = "vitna"
    POSTGRES_PASSWORD: str = "vitnap@ssw0rd"

    REDIS_PASSWORD: str = "vitnap@ssw0rd"

    MINIO_ENDPOINT: str = "ts_minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "vitnap@ssw0rd"
    MINIO_SECURE: bool = False

    LIVEKIT_URL: str = "ws://ts_livekit:7880"
    LIVEKIT_API_KEY: str = "translation_api"
    LIVEKIT_API_SECRET: str = "SecureSecret2026LiveKitKey32Chars!!"

    JWT_SECRET: str = "SecureSecret2026JWTKey32Chars!!XX"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_HOURS: int = 24

    PORT_MAIN: int = 19000
    PORT_ADMIN: int = 19080
    PORT_LISTENER: int = 19081
    PORT_INTERPRETER: int = 19082

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

    @property
    def effective_ip(self) -> str:
        return self.SERVER_IP or get_server_ip()

    @property
    def db_url(self) -> str:
        """@ 특수문자 URL 인코딩 처리"""
        pw = quote(self.POSTGRES_PASSWORD, safe='')
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{pw}@ts_postgres:5432/{self.POSTGRES_DB}"

    @property
    def redis_url(self) -> str:
        """@ 특수문자 URL 인코딩 처리"""
        pw = quote(self.REDIS_PASSWORD, safe='')
        return f"redis://:{pw}@ts_redis:6379"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

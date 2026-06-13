from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
import time
import socket

from app.config import settings
from app.database import engine
from app.redis_client import get_redis, close_redis

from app.routers import (
    websocket_router,
    auth, users, broadcasts, rooms,
    livekit_router, listeners, interpreters,
    recordings, ai_router, monitoring, audit, webhooks
)

def get_server_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

@asynccontextmanager
async def lifespan(app: FastAPI):
    ip = get_server_ip()
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 시작")
    logger.info(f"📡 서버 IP: {ip}")
    logger.info(f"🖥️  관리자 UI:  http://{ip}:{settings.PORT_ADMIN}")
    logger.info(f"🎧 청취자 UI:  http://{ip}:{settings.PORT_LISTENER}")
    logger.info(f"🎙️  통역자 UI:  http://{ip}:{settings.PORT_INTERPRETER}")
    logger.info(f"📖 API Docs:   http://{ip}:19000/api/docs")
    await get_redis()
    yield
    await close_redis()
    await engine.dispose()
    logger.info("서버 종료")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="다국어 통역방송 시스템 API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS - 테스트 환경 전체 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(round((time.time()-start)*1000, 2))
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {"code": "SYS_001", "message": "서버 내부 오류"}
        }
    )

# ★ 핵심: PREFIX = "/api/v1" 이므로
# monitoring.py 의 경로는 "/system/health" 만 적어야
# 최종 경로 "/api/v1/system/health" 가 됨
PREFIX = "/api/v1"
app.include_router(auth.router,             prefix=PREFIX)
app.include_router(users.router,            prefix=PREFIX)
app.include_router(broadcasts.router,       prefix=PREFIX)
app.include_router(rooms.router,            prefix=PREFIX)
app.include_router(livekit_router.router,   prefix=PREFIX)
app.include_router(listeners.router,        prefix=PREFIX)
app.include_router(interpreters.router,     prefix=PREFIX)
app.include_router(recordings.router,       prefix=PREFIX)
app.include_router(ai_router.router,        prefix=PREFIX)
app.include_router(monitoring.router,       prefix=PREFIX)
app.include_router(audit.router,            prefix=PREFIX)
app.include_router(webhooks.router,         prefix=PREFIX)

# WebSocket + 기존 Node.js 호환 API (prefix 없이)
app.include_router(websocket_router.router)

@app.get("/")
async def root():
    ip = get_server_ip()
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "server_ip": ip,
        "urls": {
            "portal":      f"http://{ip}:{settings.PORT_MAIN}",
            "admin":       f"http://{ip}:{settings.PORT_ADMIN}",
            "listener":    f"http://{ip}:{settings.PORT_LISTENER}",
            "interpreter": f"http://{ip}:{settings.PORT_INTERPRETER}",
            "api_docs":    f"http://{ip}:19000/api/docs",
            "grafana":     f"http://{ip}:19300",
            "minio":       f"http://{ip}:19011",
        }
    }

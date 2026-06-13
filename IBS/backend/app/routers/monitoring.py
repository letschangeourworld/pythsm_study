from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
from app.redis_client import get_redis
import time
import psutil

router = APIRouter(tags=["Monitoring"])

@router.get("/system/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """헬스 체크"""
    services = {}
    try:
        await db.execute(text("SELECT 1"))
        services["postgresql"] = "healthy"
    except Exception as e:
        services["postgresql"] = f"unhealthy: {str(e)}"
    try:
        r = await get_redis()
        await r.ping()
        services["redis"] = "healthy"
    except Exception as e:
        services["redis"] = f"unhealthy: {str(e)}"

    all_ok = all(v == "healthy" for v in services.values())
    return {
        "status": "healthy" if all_ok else "degraded",
        "timestamp": time.time(),
        "services": services,
        "version": "1.0.0"
    }

@router.get("/system/live")
async def liveness():
    return {"status": "alive"}

@router.get("/system/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Not ready")

@router.get("/system/status")
async def system_status(db: AsyncSession = Depends(get_db)):
    return await health_check(db)

@router.get("/monitoring/metrics")
async def get_metrics():
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "percent": psutil.virtual_memory().percent,
        },
        "disk": {
            "total": psutil.disk_usage('/').total,
            "free": psutil.disk_usage('/').free,
            "percent": psutil.disk_usage('/').percent,
        }
    }

@router.get("/dashboard")
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    """Dashboard KPI 데이터"""
    lr = await db.execute(text("""
        SELECT COUNT(*) FROM broadcast.listener_sessions
        WHERE disconnected_at IS NULL
          AND connected_at > NOW() - INTERVAL '10 minutes'
    """))
    br = await db.execute(text(
        "SELECT COUNT(*) FROM broadcast.sessions WHERE status='LIVE'"
    ))
    ir = await db.execute(text("""
        SELECT COUNT(*) FROM broadcast.interpreter_sessions
        WHERE logout_time IS NULL
          AND last_heartbeat > NOW() - INTERVAL '2 minutes'
    """))
    return {
        "success": True,
        "data": {
            "total_listeners": lr.scalar() or 0,
            "live_broadcasts": br.scalar() or 0,
            "active_interpreters": ir.scalar() or 0,
            "incidents": 0,
        }
    }

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db

router = APIRouter(prefix="/listeners", tags=["Listeners"])

@router.get("/count")
async def get_count(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT COUNT(*) as total,
               COUNT(CASE WHEN language_code='EN' THEN 1 END) as en,
               COUNT(CASE WHEN language_code='JA' THEN 1 END) as ja,
               COUNT(CASE WHEN language_code='ZH' THEN 1 END) as zh,
               COUNT(CASE WHEN language_code='KO' THEN 1 END) as ko
        FROM broadcast.listener_sessions
        WHERE disconnected_at IS NULL AND connected_at > NOW() - INTERVAL '10 minutes'"""))
    r = result.fetchone()
    return {"success": True, "data": {"total": r.total, "en": r.en, "ja": r.ja, "zh": r.zh, "ko": r.ko}}

@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT language_code, COUNT(*) as count
        FROM broadcast.listener_sessions
        WHERE disconnected_at IS NULL AND connected_at > NOW() - INTERVAL '10 minutes'
        GROUP BY language_code"""))
    return {"success": True, "data": [dict(r._mapping) for r in result.fetchall()]}

@router.post("/connect")
async def connect(room_name: str, language_code: str, db: AsyncSession = Depends(get_db)):
    await db.execute(text("INSERT INTO broadcast.listener_sessions(room_name,language_code) VALUES(:r,:l)"),
                     {"r": room_name, "l": language_code})
    return {"success": True}

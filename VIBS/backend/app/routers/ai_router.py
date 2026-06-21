from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
from app.routers.auth import get_current_user

router = APIRouter(prefix="/ai", tags=["AI"])

@router.get("/stt/status")
async def stt_status():
    return {"success": True, "data": {"status": "ready", "model": "faster-whisper-large-v3"}}

@router.get("/translation/status")
async def translation_status():
    return {"success": True, "data": {"status": "ready", "model": "nllb-200-3.3b"}}

@router.get("/tts/status")
async def tts_status():
    return {"success": True, "data": {"status": "ready", "model": "piper"}}

@router.get("/stt")
async def get_stt_logs(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(text("SELECT * FROM ai.stt_logs ORDER BY created_at DESC LIMIT 100"))
    return {"success": True, "data": [dict(r._mapping) for r in result.fetchall()]}

@router.post("/tm/search")
async def search_tm(source_text: str, source_lang: str = "ko", target_lang: str = "en",
                    db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT source_text, translated_text, usage_count, verified
        FROM ai.translation_memory
        WHERE source_language=:sl AND target_language=:tl AND source_text ILIKE :q
        ORDER BY usage_count DESC LIMIT 5"""),
        {"sl": source_lang, "tl": target_lang, "q": f"%{source_text}%"})
    return {"success": True, "data": [dict(r._mapping) for r in result.fetchall()]}

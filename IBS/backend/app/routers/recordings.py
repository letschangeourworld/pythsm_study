from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
from app.routers.auth import get_current_user

router = APIRouter(prefix="/recordings", tags=["Recordings"])

@router.get("/")
async def get_recordings(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(text("""
        SELECT r.*, s.title as session_title FROM broadcast.recordings r
        LEFT JOIN broadcast.sessions s ON r.session_id=s.id
        ORDER BY r.created_at DESC LIMIT 50"""))
    return {"success": True, "data": [dict(r._mapping) for r in result.fetchall()]}

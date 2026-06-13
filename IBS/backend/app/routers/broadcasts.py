from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.routers.auth import get_current_user
from app.redis_client import get_redis
from datetime import datetime
import uuid

router = APIRouter(prefix="/broadcasts", tags=["Broadcasts"])

class BroadcastCreate(BaseModel):
    title: str
    description: Optional[str] = None
    room_name: str = "room_en"

@router.get("/")
async def get_broadcasts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT s.id, s.title, s.description, s.status,
               s.start_time, s.end_time, s.created_at,
               r.room_name, r.language_code, r.language_name
        FROM broadcast.sessions s
        LEFT JOIN broadcast.rooms r ON s.room_id=r.id
        ORDER BY s.created_at DESC LIMIT 50"""))
    return {"success": True, "data": [dict(r._mapping) for r in result.fetchall()]}

@router.post("/", status_code=201)
async def create_broadcast(data: BroadcastCreate, db: AsyncSession = Depends(get_db),
                           user=Depends(get_current_user)):
    if user["role"] not in ["SUPER_ADMIN", "OPERATOR"]:
        raise HTTPException(status_code=403, detail="권한 없음")
    room = (await db.execute(text("SELECT id FROM broadcast.rooms WHERE room_name=:n"), {"n": data.room_name})).fetchone()
    if not room:
        raise HTTPException(status_code=404, detail="Room 없음")
    sid = str(uuid.uuid4())
    await db.execute(text("""
        INSERT INTO broadcast.sessions(id,room_id,title,description,status,created_by)
        VALUES(:id,:room_id,:title,:desc,'READY',:by)"""),
        {"id": sid, "room_id": str(room.id), "title": data.title, "desc": data.description, "by": user["id"]})
    return {"success": True, "data": {"id": sid, "status": "READY"}}

@router.post("/{bid}/start")
async def start_broadcast(bid: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    if user["role"] not in ["SUPER_ADMIN", "OPERATOR"]:
        raise HTTPException(status_code=403, detail="권한 없음")
    await db.execute(text("UPDATE broadcast.sessions SET status='LIVE',start_time=NOW(),updated_at=NOW() WHERE id=:id"), {"id": bid})
    r = await get_redis()
    await r.xadd("recording.events", {"event": "BROADCAST_STARTED", "session_id": bid, "ts": datetime.utcnow().isoformat()})
    return {"success": True, "message": "방송 시작"}

@router.post("/{bid}/stop")
async def stop_broadcast(bid: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    if user["role"] not in ["SUPER_ADMIN", "OPERATOR"]:
        raise HTTPException(status_code=403, detail="권한 없음")
    await db.execute(text("UPDATE broadcast.sessions SET status='ENDED',end_time=NOW(),updated_at=NOW() WHERE id=:id"), {"id": bid})
    r = await get_redis()
    await r.xadd("recording.events", {"event": "BROADCAST_ENDED", "session_id": bid})
    return {"success": True, "message": "방송 종료"}

@router.get("/{bid}")
async def get_broadcast(bid: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT s.*, r.room_name, r.language_code, r.language_name
        FROM broadcast.sessions s LEFT JOIN broadcast.rooms r ON s.room_id=r.id
        WHERE s.id=:id"""), {"id": bid})
    b = result.fetchone()
    if not b:
        raise HTTPException(status_code=404, detail="방송 없음")
    return {"success": True, "data": dict(b._mapping)}

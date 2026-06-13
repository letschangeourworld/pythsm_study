from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.routers.auth import get_current_user
import uuid

router = APIRouter(prefix="/interpreters", tags=["Interpreters"])

class SessionStart(BaseModel):
    room_name: str
    session_id: Optional[str] = None

@router.get("/")
async def get_interpreters(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(text("""
        SELECT u.id, u.username, u.full_name, is2.room_name, is2.login_time, is2.status
        FROM auth.users u
        LEFT JOIN auth.user_roles ur ON u.id=ur.user_id
        LEFT JOIN auth.roles r ON ur.role_id=r.id
        LEFT JOIN broadcast.interpreter_sessions is2 ON u.id=is2.interpreter_id AND is2.logout_time IS NULL
        WHERE r.role_name IN ('INTERPRETER','OPERATOR','SUPER_ADMIN')
          AND u.deleted_at IS NULL AND u.enabled=TRUE"""))
    return {"success": True, "data": [dict(r._mapping) for r in result.fetchall()]}

@router.post("/session/start")
async def start_session(data: SessionStart, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    sid = str(uuid.uuid4())
    await db.execute(text("""
        INSERT INTO broadcast.interpreter_sessions(id,interpreter_id,room_name,session_id,status)
        VALUES(:id,:uid,:room,:sid,'ONLINE')"""),
        {"id": sid, "uid": user["id"], "room": data.room_name, "sid": data.session_id})
    return {"success": True, "data": {"session_id": sid}}

@router.post("/session/stop")
async def stop_session(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    await db.execute(text("""
        UPDATE broadcast.interpreter_sessions SET logout_time=NOW(),status='OFFLINE'
        WHERE interpreter_id=:uid AND logout_time IS NULL"""), {"uid": user["id"]})
    return {"success": True}

@router.post("/heartbeat")
async def heartbeat(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    await db.execute(text("""
        UPDATE broadcast.interpreter_sessions SET last_heartbeat=NOW()
        WHERE interpreter_id=:uid AND logout_time IS NULL"""), {"uid": user["id"]})
    return {"success": True}

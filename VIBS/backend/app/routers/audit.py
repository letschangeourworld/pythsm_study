from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
from app.routers.auth import get_current_user

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/")
async def get_audit_logs(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    if user["role"] not in ["SUPER_ADMIN", "OPERATOR"]:
        raise HTTPException(status_code=403, detail="권한 없음")
    result = await db.execute(text("SELECT * FROM audit.audit_logs ORDER BY created_at DESC LIMIT 100"))
    return {"success": True, "data": [dict(r._mapping) for r in result.fetchall()]}

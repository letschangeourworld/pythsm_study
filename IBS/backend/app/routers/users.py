from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
from app.routers.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
async def get_users(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(text("""
        SELECT u.id, u.username, u.email, u.full_name, u.enabled, u.created_at,
               string_agg(r.role_name, ',') as roles
        FROM auth.users u
        LEFT JOIN auth.user_roles ur ON u.id=ur.user_id
        LEFT JOIN auth.roles r ON ur.role_id=r.id
        WHERE u.deleted_at IS NULL GROUP BY u.id ORDER BY u.created_at DESC"""))
    return {"success": True, "data": [dict(r._mapping) for r in result.fetchall()]}

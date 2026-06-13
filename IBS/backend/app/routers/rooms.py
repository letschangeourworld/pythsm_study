from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db

router = APIRouter(prefix="/rooms", tags=["Rooms"])

@router.get("/")
async def get_rooms(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM broadcast.rooms WHERE active=TRUE"))
    return {"success": True, "data": [dict(r._mapping) for r in result.fetchall()]}

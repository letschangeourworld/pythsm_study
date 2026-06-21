from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.database import get_db
from app.config import settings
from app.redis_client import get_redis
import uuid

router = APIRouter(prefix="/auth", tags=["Auth"])
security = HTTPBearer()

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload["jti"] = str(uuid.uuid4())
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

async def get_current_user(
    cred: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = jwt.decode(cred.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰")
    except JWTError:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰")

    result = await db.execute(
        text("SELECT id, username, enabled FROM auth.users WHERE username=:u AND deleted_at IS NULL"),
        {"u": username}
    )
    user = result.fetchone()
    if not user or not user.enabled:
        raise HTTPException(status_code=401, detail="사용자 없음")
    return {"id": str(user.id), "username": user.username, "role": payload.get("role", "VIEWER")}

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("""SELECT u.id, u.username, u.enabled, r.role_name
                FROM auth.users u
                LEFT JOIN auth.user_roles ur ON u.id=ur.user_id
                LEFT JOIN auth.roles r ON ur.role_id=r.id
                WHERE u.username=:u AND u.deleted_at IS NULL"""),
        {"u": req.username}
    )
    user = result.fetchone()
    if not user or not user.enabled:
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호 오류")

    # 테스트용 간단 인증
    valid = (req.username == "admin" and req.password == "admin123") or \
            (req.username == "interpreter_en" and req.password == "interp123")
    if not valid:
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호 오류")

    token = create_token({
        "sub": user.username,
        "user_id": str(user.id),
        "role": user.role_name or "VIEWER",
    })

    redis = await get_redis()
    await redis.xadd("audit.events", {"action": "LOGIN", "username": user.username})

    return TokenResponse(access_token=token, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES*60)

@router.get("/me")
async def get_me(user=Depends(get_current_user)):
    return {"success": True, "data": user}

@router.post("/logout")
async def logout(user=Depends(get_current_user)):
    return {"success": True, "message": "로그아웃 완료"}

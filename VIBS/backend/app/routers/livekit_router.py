from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from app.config import settings
import uuid, os, subprocess, re
from typing import Optional

router = APIRouter(prefix="/livekit", tags=["LiveKit"])
security = HTTPBearer(auto_error=False)

def get_server_ip():
    SKIP = ("172.17.","172.18.","172.19.",
            "172.21.","172.22.","172.30.","172.31.",
            "127.","10.0.0.")
    def bad(ip): return any(ip.startswith(p) for p in SKIP)
    for key in ["SERVER_IP","PUBLIC_IP"]:
        v = os.environ.get(key,"").strip()
        if v and v != "localhost" and not bad(v):
            return v
    try:
        r = subprocess.run(["hostname","-I"],
                           capture_output=True,text=True,timeout=3)
        for ip in r.stdout.split():
            if re.match(r"^\d+\.\d+\.\d+\.\d+$",ip) and not bad(ip):
                return ip
    except: pass
    return "localhost"

class TokenRequest(BaseModel):
    room: str
    identity: Optional[str] = None
    role: str = "listener"

@router.post("/token")
async def create_livekit_token(
    req: TokenRequest,
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    role = "listener"
    username = req.identity or f"listener_{str(uuid.uuid4())[:8]}"

    if req.role == "interpreter":
        role = "interpreter"
        username = req.identity or f"interp_{str(uuid.uuid4())[:8]}"
        if credentials:
            try:
                from jose import jwt as jose_jwt
                payload = jose_jwt.decode(
                    credentials.credentials,
                    settings.JWT_SECRET,
                    algorithms=[settings.JWT_ALGORITHM]
                )
                username = payload.get("sub", username)
            except Exception:
                pass

    is_publisher = (role == "interpreter")
    server_ip = get_server_ip()

    from livekit.api import AccessToken, VideoGrants
    grants = VideoGrants(
        room_join=True,
        room=req.room,
        can_publish=is_publisher,
        can_subscribe=True,
        can_publish_data=is_publisher,
    )
    tok = AccessToken(
        api_key=settings.LIVEKIT_API_KEY,
        api_secret=settings.LIVEKIT_API_SECRET
    )
    tok = tok.with_identity(username).with_grants(grants)

    return {
        "success": True,
        "data": {
            "token": tok.to_jwt(),
            "room": req.room,
            "identity": username,
            "server_url": f"ws://{server_ip}:17880",
            "is_publisher": is_publisher,
            "role": role,
        }
    }

@router.get("/rooms")
async def get_rooms():
    return {"success": True, "data": [
        {"name":"room_ko","language":"KO","label":"한국어"},
        {"name":"room_en","language":"EN","label":"English"},
        {"name":"room_ja","language":"JA","label":"日本語"},
        {"name":"room_zh","language":"ZH","label":"中文"},
    ]}

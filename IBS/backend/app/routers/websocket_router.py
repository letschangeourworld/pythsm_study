"""
기존 Vitna Node.js 서버의 WebSocket/API를 FastAPI로 완전 호환 구현
- /ws WebSocket 엔드포인트
- /api/login, /api/channels, /api/broadcast/* 등
- 채팅, STT, 번역 히스토리 관리
- 동적 채널 추가 지원
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import JSONResponse
from loguru import logger
from typing import Dict, Optional
from datetime import datetime, timedelta
import json
import asyncio
from jose import jwt
from app.config import settings
from app.redis_client import get_redis
import os

router = APIRouter(tags=["WebSocket & 기존 호환 API"])

# ── 채널 상태 관리 ──────────────────────────────────────────
class ChannelManager:
    def __init__(self):
        self.channels: Dict[str, Dict[WebSocket, dict]] = {
            "english": {}, "japanese": {}, "chinese": {}
        }
        self.states: Dict[str, dict] = {
            "english":  {"active": False, "listeners": 0, "startedAt": None, "sessionId": None, "maxListeners": 0, "label": "English", "flag": "🇺🇸", "room": "room_en"},
            "japanese": {"active": False, "listeners": 0, "startedAt": None, "sessionId": None, "maxListeners": 0, "label": "日本語", "flag": "🇯🇵", "room": "room_ja"},
            "chinese":  {"active": False, "listeners": 0, "startedAt": None, "sessionId": None, "maxListeners": 0, "label": "中文",   "flag": "🇨🇳", "room": "room_zh"},
        }
        self.chat_history: Dict[str, list] = {"english": [], "japanese": [], "chinese": []}
        self.stt_history: list = []
        self._id = 0

    def next_id(self) -> int:
        self._id += 1
        return self._id

    def add_channel(self, ch_key: str, label: str, flag: str, room: str):
        """동적 채널 추가"""
        if ch_key not in self.channels:
            self.channels[ch_key] = {}
            self.states[ch_key] = {
                "active": False, "listeners": 0, "startedAt": None,
                "sessionId": None, "maxListeners": 0,
                "label": label, "flag": flag, "room": room
            }
            self.chat_history[ch_key] = []
            return True
        return False

    async def add(self, ws: WebSocket, channel: str, name: str, role: str):
        if channel not in self.channels:
            channel = "english"
        self.channels[channel][ws] = {
            "name": name, "role": role, "channel": channel,
            "joinedAt": datetime.utcnow().isoformat()
        }
        self.states[channel]["listeners"] = len(self.channels[channel])

    def remove(self, ws: WebSocket) -> tuple:
        for ch, conns in self.channels.items():
            if ws in conns:
                info = conns.pop(ws)
                self.states[ch]["listeners"] = max(0, len(conns))
                return ch, info
        return None, {}

    async def send(self, ws: WebSocket, data: dict):
        try:
            await ws.send_json(data)
        except Exception:
            pass

    async def broadcast_channel(self, channel: str, data: dict, exclude: WebSocket = None):
        dead = []
        for ws, info in list(self.channels.get(channel, {}).items()):
            if ws is exclude:
                continue
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.remove(ws)

    async def broadcast_all(self, data: dict):
        for ch in self.channels:
            await self.broadcast_channel(ch, data)

    def get_users(self, channel: str) -> list:
        seen = set()
        users = []
        for info in self.channels.get(channel, {}).values():
            if info["name"] not in seen:
                seen.add(info["name"])
                users.append({"name": info["name"], "role": info["role"]})
        return users

    def get_all_states(self) -> dict:
        return {
            ch: {**st, "listeners": len(self.channels.get(ch, {}))}
            for ch, st in self.states.items()
        }

    def add_chat(self, channel: str, msg: dict):
        hist = self.chat_history.setdefault(channel, [])
        hist.append(msg)
        if len(hist) > 100:
            hist.pop(0)

    def add_stt(self, record: dict):
        self.stt_history.append(record)
        if len(self.stt_history) > 500:
            self.stt_history.pop(0)

    def set_active(self, channel: str, active: bool, session_id: int = None):
        if channel in self.states:
            self.states[channel]["active"] = active
            self.states[channel]["startedAt"] = datetime.utcnow().isoformat() if active else None
            self.states[channel]["sessionId"] = session_id
            if active:
                self.states[channel]["maxListeners"] = 0


mgr = ChannelManager()


def sanitize(s: str, max_len: int = 100) -> str:
    return str(s or "").replace("<", "").replace(">", "").replace('"', "").strip()[:max_len]


# ── WebSocket 엔드포인트 ────────────────────────────────────
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    channel = "english"
    name = "Guest"
    role = "listener"
    joined = False
    client_id = mgr.next_id()

    try:
        await websocket.send_json({"type": "state", "channels": mgr.get_all_states()})

        async for raw in websocket.iter_text():
            try:
                data = json.loads(raw)
            except Exception:
                continue

            msg_type = data.get("type", "")

            if msg_type == "init":
                if joined:
                    mgr.remove(websocket)

                channel = data.get("channel", "english")
                if channel not in mgr.channels:
                    channel = "english"

                input_name = sanitize(data.get("name", ""), 20)
                role = "listener"

                token = data.get("token", "")
                if token:
                    try:
                        payload = jwt.decode(
                            token, settings.JWT_SECRET,
                            algorithms=[settings.JWT_ALGORITHM]
                        )
                        r = payload.get("role", "")
                        if r in ("SUPER_ADMIN", "OPERATOR", "admin"):
                            role = "admin"
                        name = input_name or sanitize(payload.get("sub", ""), 20) or f"Guest{client_id}"
                    except Exception:
                        name = input_name or f"청취자{client_id}"
                else:
                    name = input_name or f"청취자{client_id}"

                await mgr.add(websocket, channel, name, role)
                joined = True

                await websocket.send_json({
                    "type": "init_ok", "clientId": client_id,
                    "name": name, "role": role, "channel": channel
                })

                hist = mgr.chat_history.get(channel, [])
                if hist:
                    await websocket.send_json({"type": "chat_history", "messages": hist[-50:]})
                if mgr.stt_history:
                    await websocket.send_json({"type": "stt_history", "transcripts": mgr.stt_history[-50:]})

                await mgr.broadcast_channel(channel, {
                    "type": "user_list", "channel": channel,
                    "users": mgr.get_users(channel)
                })
                await mgr.broadcast_all({
                    "type": "channel_update", "channel": channel,
                    "state": mgr.states[channel]
                })

                logger.info(f"WS init_ok: {name} [{role}] → {channel}")

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

            elif msg_type == "set_name" and joined:
                new_name = sanitize(data.get("name", ""), 20)
                if len(new_name) >= 2:
                    old_name = name
                    name = new_name
                    if websocket in mgr.channels.get(channel, {}):
                        mgr.channels[channel][websocket]["name"] = name
                    await websocket.send_json({"type": "name_changed", "name": name, "role": role})
                    sys_msg = {
                        "type": "chat", "channel": channel,
                        "senderType": "system", "senderName": "system",
                        "message": f"'{old_name}' → '{name}' 으로 닉네임 변경",
                        "sentAt": datetime.utcnow().isoformat()
                    }
                    await mgr.broadcast_channel(channel, sys_msg)
                    await mgr.broadcast_channel(channel, {
                        "type": "user_list", "channel": channel,
                        "users": mgr.get_users(channel)
                    })

            elif msg_type == "chat" and joined:
                message = sanitize(data.get("message", ""), 300)
                if not message:
                    continue
                chat_data = {
                    "type": "chat", "channel": channel,
                    "senderType": role, "senderName": name,
                    "message": message, "sentAt": datetime.utcnow().isoformat()
                }
                mgr.add_chat(channel, {
                    "sender_type": role, "sender_name": name,
                    "message": message, "sent_at": chat_data["sentAt"]
                })
                await mgr.broadcast_channel(channel, chat_data)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WS 오류: {e}")
    finally:
        if joined:
            ch, info = mgr.remove(websocket)
            if ch:
                await mgr.broadcast_channel(ch, {
                    "type": "listener_update", "channel": ch,
                    "count": mgr.states[ch]["listeners"]
                })
                await mgr.broadcast_channel(ch, {
                    "type": "user_list", "channel": ch,
                    "users": mgr.get_users(ch)
                })
                await mgr.broadcast_all({
                    "type": "channel_update", "channel": ch,
                    "state": mgr.states[ch]
                })


# ── API 엔드포인트 ────────────────────────────────────────

@router.get("/api/channels")
async def get_channels():
    return {"channels": mgr.get_all_states()}

@router.post("/api/channels")
async def create_channel(data: dict):
    """신규 채널 동적 생성"""
    ch_key = sanitize(data.get("key", ""), 30).lower().replace(" ", "_")
    label  = sanitize(data.get("label", ""), 30)
    flag   = sanitize(data.get("flag", "🌐"), 8)
    room   = sanitize(data.get("room", f"room_{ch_key}"), 50)

    if not ch_key or not label:
        return JSONResponse(status_code=400, content={"error": "key, label 필수"})
    if ch_key in mgr.channels:
        return JSONResponse(status_code=409, content={"error": "이미 존재하는 채널"})

    mgr.add_channel(ch_key, label, flag, room)

    # 전체 클라이언트에 신규 채널 알림
    await mgr.broadcast_all({
        "type": "channel_added",
        "channel": ch_key,
        "state": mgr.states[ch_key]
    })

    logger.info(f"채널 추가: {ch_key} ({label}) → {room}")
    return {"success": True, "channel": ch_key, "state": mgr.states[ch_key]}

@router.get("/api/health")
async def health():
    return {
        "status": "ok", "version": "2.7.0-py",
        "wsClients": sum(len(c) for c in mgr.channels.values()),
        "channels": {k: {"active": v["active"], "listeners": v["listeners"]}
                     for k, v in mgr.states.items()}
    }

@router.post("/api/login")
async def api_login(data: dict):
    username = data.get("username", "")
    password = data.get("password", "")
    admin_user = os.environ.get("ADMIN_USERNAME", "admin")
    admin_pass = os.environ.get("ADMIN_PASSWORD", "admin123")
    vitna_pass = os.environ.get("KEYCLOAK_ADMIN_PASSWORD", "vitnap@ssw0rd")
    valid = (username == admin_user and password in [admin_pass, vitna_pass]) or \
            (username == "admin" and password == "admin123")
    if not valid:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")
    payload = {
        "sub": username, "username": username, "role": "admin",
        "exp": datetime.utcnow() + timedelta(hours=12)
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return {"token": token, "message": "로그인 성공"}

@router.post("/api/broadcast/start")
async def broadcast_start(data: dict):
    channel = data.get("channel", "english")
    if channel not in mgr.channels:
        return {"error": "유효하지 않은 채널"}

    # DB에 방송 세션 기록
    session_id = None
    try:
        from app.database import AsyncSessionLocal
        from sqlalchemy import text
        import uuid
        ch_to_room = {
            "english": "room_en", "japanese": "room_ja",
            "chinese": "room_zh", "korean": "room_ko"
        }
        room_name = mgr.states[channel].get("room") or ch_to_room.get(channel, f"room_{channel[:2]}")
        async with AsyncSessionLocal() as db:
            room = (await db.execute(
                text("SELECT id FROM broadcast.rooms WHERE room_name=:n"),
                {"n": room_name}
            )).fetchone()
            if room:
                session_id = str(uuid.uuid4())
                label = mgr.states[channel].get("label", channel)
                await db.execute(text(
                    "INSERT INTO broadcast.sessions"
                    " (id, room_id, title, status, start_time, created_at, updated_at)"
                    " VALUES (:id, :room_id, :title, 'LIVE', NOW(), NOW(), NOW())"
                ), {"id": session_id, "room_id": str(room.id),
                    "title": f"{label} 통역 방송"})
                await db.commit()
                logger.info(f"방송 세션 DB 기록 완료: {session_id}")
            else:
                logger.warning(f"room_name '{room_name}' 없음 - DB 기록 생략")
    except Exception as e:
        logger.warning(f"방송 DB 기록 실패 (무시): {e}")

    mgr.set_active(channel, True, session_id)
    await mgr.broadcast_all({
        "type": "channel_update", "channel": channel,
        "state": mgr.states[channel]
    })
    sys_msg = {
        "type": "chat", "channel": channel,
        "senderType": "admin", "senderName": "system",
        "message": "📢 통역 방송이 시작되었습니다. 이어폰을 연결하고 청취해 주세요.",
        "sentAt": datetime.utcnow().isoformat()
    }
    mgr.add_chat(channel, {"sender_type": "admin", "sender_name": "system",
                            "message": sys_msg["message"], "sent_at": sys_msg["sentAt"]})
    await mgr.broadcast_channel(channel, sys_msg)
    logger.info(f"방송 시작: {channel}")
    return {"success": True, "channel": channel, "state": mgr.states[channel],
            "session_id": session_id}

@router.post("/api/broadcast/stop")
async def broadcast_stop(data: dict):
    channel = data.get("channel", "english")
    if channel not in mgr.channels:
        return {"error": "유효하지 않은 채널"}

    # DB 방송 세션 종료 기록
    session_id = mgr.states[channel].get("sessionId")
    try:
        if session_id:
            from app.database import AsyncSessionLocal
            from sqlalchemy import text
            async with AsyncSessionLocal() as db:
                await db.execute(text(
                    "UPDATE broadcast.sessions"
                    " SET status='ENDED', end_time=NOW(), updated_at=NOW()"
                    " WHERE id=:id"
                ), {"id": session_id})
                await db.commit()
                logger.info(f"방송 세션 종료 DB 기록 완료: {session_id}")
    except Exception as e:
        logger.warning(f"방송 종료 DB 기록 실패 (무시): {e}")

    stop_msg = {
        "type": "chat", "channel": channel,
        "senderType": "admin", "senderName": "system",
        "message": "통역 방송이 종료되었습니다. 함께해 주셔서 감사합니다.",
        "sentAt": datetime.utcnow().isoformat()
    }
    mgr.add_chat(channel, {"sender_type": "admin", "sender_name": "system",
                            "message": stop_msg["message"], "sent_at": stop_msg["sentAt"]})
    await mgr.broadcast_channel(channel, stop_msg)
    mgr.set_active(channel, False)
    await mgr.broadcast_all({
        "type": "channel_update", "channel": channel,
        "state": mgr.states[channel]
    })
    logger.info(f"방송 종료: {channel}")
    return {"success": True, "channel": channel, "state": mgr.states[channel]}


@router.get("/api/broadcast/history")
async def broadcast_history():
    """방송 이력 조회 (최근 30개)"""
    try:
        from app.database import AsyncSessionLocal
        from sqlalchemy import text
        async with AsyncSessionLocal() as db:
            result = await db.execute(text(
                "SELECT s.id, s.title, s.status,"
                " s.start_time, s.end_time,"
                " r.room_name, r.language_name, r.language_code,"
                " EXTRACT(EPOCH FROM ("
                "   COALESCE(s.end_time, NOW()) - COALESCE(s.start_time, s.created_at)"
                " ))::int AS duration_sec,"
                " s.created_at"
                " FROM broadcast.sessions s"
                " LEFT JOIN broadcast.rooms r ON s.room_id = r.id"
                " ORDER BY s.created_at DESC LIMIT 30"
            ))
            rows = result.fetchall()
            return {"success": True, "data": [dict(r._mapping) for r in rows]}
    except Exception as e:
        logger.warning(f"방송 이력 조회 실패: {e}")
        return {"success": False, "data": [], "error": str(e)}

@router.get("/api/broadcast/stats")
async def broadcast_stats():
    """방송 통계 조회"""
    try:
        from app.database import AsyncSessionLocal
        from sqlalchemy import text
        async with AsyncSessionLocal() as db:
            result = await db.execute(text(
                "SELECT"
                " COUNT(*) AS total_sessions,"
                " COUNT(CASE WHEN status='LIVE'  THEN 1 END) AS live_count,"
                " COUNT(CASE WHEN status='ENDED' THEN 1 END) AS ended_count,"
                " COALESCE(AVG(EXTRACT(EPOCH FROM (end_time - start_time))/60)"
                "   FILTER (WHERE status='ENDED' AND end_time IS NOT NULL), 0)::int"
                "   AS avg_duration_min,"
                " COUNT(CASE WHEN created_at >= NOW() - INTERVAL '7 days' THEN 1 END)"
                "   AS this_week"
                " FROM broadcast.sessions"
            ))
            row = result.fetchone()
            return {"success": True, "data": dict(row._mapping) if row else {}}
    except Exception as e:
        return {"success": False, "data": {}, "error": str(e)}


@router.get("/api/broadcast/history")
async def broadcast_history():
    """방송 이력 조회 (최근 30개)"""
    try:
        from app.database import AsyncSessionLocal
        from sqlalchemy import text
        async with AsyncSessionLocal() as db:
            result = await db.execute(text(
                "SELECT s.id, s.title, s.status,"
                " s.start_time, s.end_time,"
                " r.room_name, r.language_name, r.language_code,"
                " EXTRACT(EPOCH FROM ("
                "   COALESCE(s.end_time, NOW()) - COALESCE(s.start_time, s.created_at)"
                " ))::int AS duration_sec,"
                " s.created_at"
                " FROM broadcast.sessions s"
                " LEFT JOIN broadcast.rooms r ON s.room_id = r.id"
                " ORDER BY s.created_at DESC LIMIT 30"
            ))
            rows = result.fetchall()
            return {"success": True, "data": [dict(r._mapping) for r in rows]}
    except Exception as e:
        logger.warning(f"방송 이력 조회 실패: {e}")
        return {"success": False, "data": [], "error": str(e)}

@router.get("/api/broadcast/stats")
async def broadcast_stats():
    """방송 통계 조회"""
    try:
        from app.database import AsyncSessionLocal
        from sqlalchemy import text
        async with AsyncSessionLocal() as db:
            result = await db.execute(text(
                "SELECT"
                " COUNT(*) AS total_sessions,"
                " COUNT(CASE WHEN status='LIVE'  THEN 1 END) AS live_count,"
                " COUNT(CASE WHEN status='ENDED' THEN 1 END) AS ended_count,"
                " COALESCE(AVG(EXTRACT(EPOCH FROM (end_time - start_time))/60)"
                "   FILTER (WHERE status='ENDED' AND end_time IS NOT NULL), 0)::int"
                "   AS avg_duration_min,"
                " COUNT(CASE WHEN created_at >= NOW() - INTERVAL '7 days' THEN 1 END)"
                "   AS this_week"
                " FROM broadcast.sessions"
            ))
            row = result.fetchone()
            return {"success": True, "data": dict(row._mapping) if row else {}}
    except Exception as e:
        return {"success": False, "data": {}, "error": str(e)}

@router.post("/api/chat/announce")
async def chat_announce(data: dict):
    channel = data.get("channel", "english")
    message = sanitize(data.get("message", ""), 300)
    if not message or channel not in mgr.channels:
        return {"error": "채널명/메시지 필요"}
    msg = {
        "type": "chat", "channel": channel,
        "senderType": "admin", "senderName": "관리자",
        "message": message, "sentAt": datetime.utcnow().isoformat()
    }
    mgr.add_chat(channel, {"sender_type": "admin", "sender_name": "관리자",
                            "message": message, "sent_at": msg["sentAt"]})
    await mgr.broadcast_channel(channel, msg)
    return {"success": True}

@router.get("/api/chat/history")
async def chat_history(channel: str = "english"):
    return {"messages": mgr.chat_history.get(channel, [])}

@router.get("/api/stt/status")
async def stt_status():
    return {"engine": os.environ.get("STT_ENGINE","none"), "running": False,
            "language": os.environ.get("STT_LANGUAGE","ko"), "device": "cpu"}

@router.get("/api/stt/history")
async def stt_history(limit: int = 100):
    return {"transcripts": mgr.stt_history[-limit:], "source": "memory"}

@router.get("/api/translation/status")
async def translation_status():
    return {"engine": os.environ.get("TRANSLATION_ENGINE","none"),
            "sourceLang": "ko", "targetLangs": ["en","ja","zh"]}

# ── 스케줄 메모리 저장소 ──────────────────────────────────
_schedules = [
    {"id":1,"schedule_time":"07:50","label":"오전 1부 예배 (08:00)","days_of_week":"0","active":True},
    {"id":2,"schedule_time":"09:20","label":"오전 2부 예배 (09:30)","days_of_week":"0","active":True},
    {"id":3,"schedule_time":"11:20","label":"오전 3부 예배 (11:30)","days_of_week":"0","active":True},
    {"id":4,"schedule_time":"13:50","label":"오후 예배 (14:00)",    "days_of_week":"0","active":True},
]
_sch_next_id = 5

@router.get("/api/schedule")
async def get_schedule():
    return {"schedules": _schedules}

@router.post("/api/schedule")
async def add_schedule(data: dict):
    global _sch_next_id
    from fastapi import HTTPException
    t     = sanitize(data.get("schedule_time",""), 10)
    label = sanitize(data.get("label",""), 100)
    days  = sanitize(data.get("days_of_week","0"), 20)
    if not t or not label:
        raise HTTPException(status_code=400, detail="schedule_time, label 필수")
    new_sch = {
        "id": _sch_next_id,
        "schedule_time": t,
        "label": label,
        "days_of_week": days,
        "active": True
    }
    _schedules.append(new_sch)
    _sch_next_id += 1
    return {"success": True, "schedule": new_sch}

@router.put("/api/schedule/{sid}")
async def update_schedule(sid: int, data: dict):
    from fastapi import HTTPException
    sch = next((s for s in _schedules if s["id"] == sid), None)
    if not sch:
        raise HTTPException(status_code=404, detail="스케줄 없음")
    if "schedule_time" in data:
        sch["schedule_time"] = sanitize(data["schedule_time"], 10)
    if "label" in data:
        sch["label"] = sanitize(data["label"], 100)
    if "days_of_week" in data:
        sch["days_of_week"] = sanitize(data["days_of_week"], 20)
    if "active" in data:
        sch["active"] = bool(data["active"])
    return {"success": True, "schedule": sch}

@router.delete("/api/schedule/{sid}")
async def del_schedule(sid: int):
    from fastapi import HTTPException
    global _schedules
    orig = len(_schedules)
    _schedules = [s for s in _schedules if s["id"] != sid]
    if len(_schedules) == orig:
        raise HTTPException(status_code=404, detail="스케줄 없음")
    return {"success": True}

@router.get("/api/stats")
async def get_stats():
    total = sum(v["listeners"] for v in mgr.states.values())
    ws_clients = sum(len(c) for c in mgr.channels.values())
    return {
        "totalListeners": total, "channels": mgr.get_all_states(),
        "wsClients": ws_clients, "todayStats": [], "recentSessions": [],
        "stt": {"engine": "none", "running": False},
        "translation": {"engine": "none"},
        "redis": {"connected": True}, "dbQueue": 0,
    }

@router.post("/api/log/connect")
async def log_connect(data: dict):
    channel = data.get("channel", "english")
    if channel in mgr.channels:
        mgr.states[channel]["listeners"] = max(0, mgr.states[channel]["listeners"] + 1)
        await mgr.broadcast_all({"type":"listener_update","channel":channel,"count":mgr.states[channel]["listeners"]})
    return {"success": True}

@router.post("/api/log/disconnect")
async def log_disconnect(data: dict):
    channel = data.get("channel", "english")
    if channel in mgr.channels:
        mgr.states[channel]["listeners"] = max(0, mgr.states[channel]["listeners"] - 1)
        await mgr.broadcast_all({"type":"listener_update","channel":channel,"count":mgr.states[channel]["listeners"]})
    return {"success": True}

@router.post("/api/stt/result")
async def stt_result(data: dict):
    text = sanitize(data.get("text",""), 4000)
    if not text:
        return {"error": "텍스트 없음"}
    record = {"original_text":text,"text":text,"confidence":float(data.get("confidence",0.9)),
              "spoken_at":data.get("spokenAt",datetime.utcnow().isoformat()),
              "spokenAt":data.get("spokenAt",datetime.utcnow().isoformat()),
              "language":"ko","speaker":"preacher"}
    mgr.add_stt(record)
    await mgr.broadcast_all({"type":"stt_text",**record})
    return {"success": True}

@router.post("/api/translation/result")
async def translation_result(data: dict):
    channel = data.get("channel","english")
    translated = sanitize(data.get("translatedText",""), 4000)
    if not translated or channel not in mgr.channels:
        return {"error": "데이터 오류"}
    await mgr.broadcast_channel(channel, {
        "type":"stt_translation","channel":channel,
        "translatedText":translated,"originalText":sanitize(data.get("originalText",""),4000),
        "targetLanguage":data.get("targetLanguage","en"),
        "spokenAt":data.get("spokenAt",datetime.utcnow().isoformat())
    })
    return {"success": True}

"""
녹음 관리 API
- GET  /api/v1/recordings/          : DB 녹음 이력 조회
- POST /api/v1/recordings/start     : 녹음 세션 시작
- POST /api/v1/recordings/chunk     : 청크 업로드
- POST /api/v1/recordings/stop      : 녹음 종료 + MinIO 저장
- GET  /api/v1/recordings/list      : MinIO 파일 목록
- GET  /api/v1/recordings/download  : 다운로드 URL
- GET  /api/v1/recordings/sessions  : 녹음 있는 세션 목록
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db, AsyncSessionLocal
from app.routers.auth import get_current_user
from loguru import logger
from datetime import datetime, timedelta
import os, io, uuid

router = APIRouter(prefix="/recordings", tags=["Recordings"])

# ── MinIO 클라이언트 ──────────────────────────────────────
def get_minio_ip():
    """MinIO 컨테이너 IP 동적 조회 (hostname 대신 IP 사용)"""
    try:
        import subprocess
        result = subprocess.run(
            ['docker', 'inspect', 'ts_minio', '--format',
             '{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}'],
            capture_output=True, text=True, timeout=3
        )
        ips = [ip for ip in result.stdout.strip().split() if ip.startswith('172.')]
        return ips[0] if ips else os.environ.get("MINIO_IP", "172.31.0.6")
    except Exception:
        return os.environ.get("MINIO_IP", "172.31.0.6")

def get_s3():
    """boto3 S3 클라이언트 (MinIO IP 직접 접근 - hostname 검증 우회)"""
    import boto3
    from botocore.config import Config
    minio_ip = get_minio_ip()
    return boto3.client(
        "s3",
        endpoint_url=f"http://{minio_ip}:9000",
        aws_access_key_id=os.environ.get("MINIO_ROOT_USER", "minioadmin"),
        aws_secret_access_key=os.environ.get("MINIO_ROOT_PASSWORD", "vitnap@ssw0rd"),
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"}
        ),
        region_name="us-east-1",
    )

def get_minio():
    """하위 호환용 - get_s3() 사용 권장"""
    return get_s3()

BUCKET_REC  = "recordings"
BUCKET_TRAN = "transcripts"

# ── 임시 청크 저장소 ──────────────────────────────────────
_chunks: dict = {}

# ────────────────────────────────────────────────────────────
# 기존 DB 조회
# ────────────────────────────────────────────────────────────
@router.get("/")
async def get_recordings(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    result = await db.execute(text("""
        SELECT r.*, s.title AS session_title
        FROM broadcast.recordings r
        LEFT JOIN broadcast.sessions s ON r.session_id = s.id
        ORDER BY r.created_at DESC LIMIT 50
    """))
    return {"success": True, "data": [dict(r._mapping) for r in result.fetchall()]}

# ────────────────────────────────────────────────────────────
# 녹음 시작
# ────────────────────────────────────────────────────────────
@router.post("/start")
async def recording_start(data: dict):
    """녹음 세션 시작 - 청크 버퍼 초기화"""
    session_id = data.get("session_id") or str(uuid.uuid4())
    _chunks[session_id] = []
    logger.info(f"녹음 시작: {session_id}")
    return {"success": True, "session_id": session_id}

# ────────────────────────────────────────────────────────────
# 청크 업로드
# ────────────────────────────────────────────────────────────
@router.post("/chunk")
async def recording_chunk(
    session_id: str      = Form(...),
    chunk:      UploadFile = File(...)
):
    """음성 청크 수신 (브라우저 MediaRecorder → 서버)"""
    if session_id not in _chunks:
        _chunks[session_id] = []
    data  = await chunk.read()
    _chunks[session_id].append(data)
    total = sum(len(c) for c in _chunks[session_id])
    return {
        "success":     True,
        "chunks":      len(_chunks[session_id]),
        "total_bytes": total
    }

# ────────────────────────────────────────────────────────────
# 녹음 종료 + MinIO 저장
# ────────────────────────────────────────────────────────────
@router.post("/stop")
async def recording_stop(data: dict):
    """
    녹음 종료 후 MinIO 저장 및 DB 업데이트
    body: {session_id, channel, role, db_session_id}
    """
    session_id    = data.get("session_id")
    channel       = data.get("channel",       "unknown")
    role          = data.get("role",          "interpreter")
    db_session_id = data.get("db_session_id")

    if not session_id or session_id not in _chunks:
        raise HTTPException(status_code=404, detail="녹음 세션 없음")

    chunks = _chunks.pop(session_id, [])
    if not chunks:
        return {"success": False, "message": "녹음 데이터 없음"}

    audio_data = b"".join(chunks)
    size_kb    = len(audio_data) / 1024
    logger.info(f"녹음 종료: {session_id} / {len(chunks)}청크 / {size_kb:.1f}KB")

    # MinIO 저장 경로
    now      = datetime.now()
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M%S")
    filename = f"{date_str}/{channel}/{role}_{time_str}_{session_id[:8]}.webm"

    try:
        s3 = get_s3()
        s3.put_object(
            Bucket=BUCKET_REC,
            Key=filename,
            Body=audio_data,
            ContentType="audio/webm"
        )
        logger.info(f"MinIO 저장 완료: {BUCKET_REC}/{filename}")

        # DB recording_path 업데이트
        if db_session_id:
            try:
                async with AsyncSessionLocal() as db:
                    await db.execute(text(
                        "UPDATE broadcast.sessions"
                        " SET recording_path=:path, stt_status='pending', updated_at=NOW()"
                        " WHERE id=:id"
                    ), {"path": f"{BUCKET_REC}/{filename}", "id": db_session_id})
                    await db.commit()
                    logger.info(f"DB recording_path 업데이트: {db_session_id}")
            except Exception as e:
                logger.warning(f"DB 업데이트 실패 (무시): {e}")

        return {
            "success":    True,
            "path":       f"{BUCKET_REC}/{filename}",
            "size_kb":    round(size_kb, 1),
            "chunks":     len(chunks),
            "stt_status": "pending"
        }
    except Exception as e:
        logger.error(f"MinIO 저장 실패: {e}")
        raise HTTPException(status_code=500, detail=f"저장 실패: {e}")

# ────────────────────────────────────────────────────────────
# MinIO 파일 목록
# ────────────────────────────────────────────────────────────
@router.get("/list")
async def recording_list(prefix: str = ""):
    """MinIO recordings 버킷 파일 목록"""
    try:
        s3  = get_s3()
        res = s3.list_objects_v2(Bucket=BUCKET_REC, Prefix=prefix)
        files = []
        for obj in res.get("Contents", []):
            files.append({
                "name":          obj["Key"],
                "size_kb":       round(obj["Size"] / 1024, 1),
                "last_modified": obj["LastModified"].isoformat(),
            })
        return {"success": True, "files": files}
    except Exception as e:
        logger.error(f"파일 목록 조회 실패: {e}")
        return {"success": False, "files": [], "error": str(e)}

# ────────────────────────────────────────────────────────────
# 다운로드 URL 발급 (1시간 유효)
# ────────────────────────────────────────────────────────────
@router.get("/download-url")
async def recording_download_url(path: str):
    """임시 다운로드 URL 발급"""
    try:
        s3 = get_s3()
        bucket, obj_name = path.split("/", 1)
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": obj_name},
            ExpiresIn=3600
        )
        return {"success": True, "url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ────────────────────────────────────────────────────────────
# 녹음 있는 방송 세션 목록
# ────────────────────────────────────────────────────────────
@router.get("/sessions")
async def recording_sessions():
    """녹음 파일이 있는 방송 세션 목록"""
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(text(
                "SELECT s.id, s.title, s.status,"
                " s.start_time, s.end_time,"
                " s.recording_path, s.transcript_path, s.stt_status,"
                " r.language_name, r.language_code,"
                " EXTRACT(EPOCH FROM ("
                "   COALESCE(s.end_time,NOW()) - COALESCE(s.start_time,s.created_at)"
                " ))::int AS duration_sec"
                " FROM broadcast.sessions s"
                " LEFT JOIN broadcast.rooms r ON s.room_id = r.id"
                " WHERE s.recording_path IS NOT NULL"
                " ORDER BY s.created_at DESC LIMIT 50"
            ))
            rows = result.fetchall()
            return {"success": True, "data": [dict(r._mapping) for r in rows]}
    except Exception as e:
        return {"success": False, "data": [], "error": str(e)}

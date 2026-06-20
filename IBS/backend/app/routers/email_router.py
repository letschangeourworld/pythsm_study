"""
이메일 전송 API
"""
from fastapi import APIRouter, BackgroundTasks, HTTPException
from loguru import logger
from datetime import datetime
import os, io, smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

router = APIRouter(prefix="/email", tags=["Email"])

# ── SMTP 설정 (함수 호출 시 동적으로 읽음) ─────────────────
def get_smtp_config():
    host  = os.environ.get("SMTP_HOST",     "smtp.naver.com")
    port  = int(os.environ.get("SMTP_PORT", "465"))
    sid   = os.environ.get("SMTP_USER",     "ndbb2046")
    pw    = os.environ.get("SMTP_PASSWORD", "ME94TGJ31GU6")
    frm   = f"{sid}@naver.com"
    return host, port, sid, pw, frm

# 하위 호환용 (모듈 레벨)
SMTP_HOST  = os.environ.get("SMTP_HOST",     "smtp.naver.com")
SMTP_PORT  = int(os.environ.get("SMTP_PORT", "465"))
SMTP_ID    = os.environ.get("SMTP_USER",     "ndbb2046")
SMTP_PASS  = os.environ.get("SMTP_PASSWORD", "ME94TGJ31GU6")
SMTP_FROM  = f"{SMTP_ID}@naver.com"

# ── 수신자 목록 (채널별) ──────────────────────────────────
RECIPIENTS = {
    "english":  [{"name": "영어 통역자",  "email": "ndbb2046@naver.com"}],
    "japanese": [{"name": "일본어 통역자","email": "ndbb2046@naver.com"}],
    "chinese":  [{"name": "중국어 통역자","email": "ndbb2046@naver.com"}],
}

# ── 전송 이력 ─────────────────────────────────────────────
_email_history = []

# ── MinIO S3 클라이언트 ───────────────────────────────────
def get_s3():
    """boto3 S3 클라이언트 - 환경변수로 MinIO IP 직접 설정"""
    import boto3
    from botocore.config import Config
    ip = os.environ.get("MINIO_IP", "172.31.0.4")
    return boto3.client(
        "s3",
        endpoint_url=f"http://{ip}:9000",
        aws_access_key_id=os.environ.get("MINIO_ROOT_USER", "minioadmin"),
        aws_secret_access_key=os.environ.get("MINIO_ROOT_PASSWORD", "vitnap@ssw0rd"),
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
        region_name="us-east-1",
    )

# ────────────────────────────────────────────────────────────
# 이메일 전송 핵심 함수
# ────────────────────────────────────────────────────────────
def send_email_with_attachment(
    to_email: str,
    to_name:  str,
    subject:  str,
    body:     str,
    attachment_data: bytes = None,
    attachment_name: str   = None
) -> bool:
    try:
        # 매번 환경변수에서 새로 읽기
        _host, _port, _sid, _pw, _from = get_smtp_config()

        msg = MIMEMultipart()
        msg['From']    = f"IBS-Broadcast <{_from}>"
        msg['To']      = f"{to_name} <{to_email}>"
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html', 'utf-8'))

        if attachment_data and attachment_name:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment_data)
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename="{attachment_name}"'
            )
            msg.attach(part)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(_host, _port, context=context) as server:
            server.login(_from, _pw)
            server.sendmail(_from, to_email, msg.as_string())

        logger.info(f"✅ 이메일 전송 완료: {to_email} / {subject}")
        return True

    except Exception as e:
        logger.error(f"❌ 이메일 전송 실패: {to_email} / {e}")
        return False

# ────────────────────────────────────────────────────────────
# 백그라운드 전송 작업
# ────────────────────────────────────────────────────────────
async def send_transcript_job(
    docx_path:  str,
    recipients: list,
    channel:    str,
    title:      str
):
    try:
        s3 = get_s3()
        bucket, key = docx_path.split("/", 1)
        buf = io.BytesIO()
        s3.download_fileobj(bucket, key, buf)
        docx_bytes = buf.getvalue()
        filename   = key.split("/")[-1]

        now     = datetime.now()
        date_kr = now.strftime("%Y년 %m월 %d일")
        subject = f"[IBS 통역방송] {date_kr} {title} 스크립트"

        body = f"""
        <html><body style="font-family:Arial,sans-serif;color:#333">
        <h2 style="color:#2563EB">📋 통역방송 스크립트 전달</h2>
        <hr>
        <p>안녕하세요,</p>
        <p>오늘({date_kr}) <strong>{title}</strong> 통역방송 스크립트를 전달드립니다.</p>
        <table style="border-collapse:collapse;margin:16px 0">
          <tr>
            <td style="padding:6px 12px;background:#f3f4f6;font-weight:bold">날짜</td>
            <td style="padding:6px 12px">{date_kr}</td>
          </tr>
          <tr>
            <td style="padding:6px 12px;background:#f3f4f6;font-weight:bold">채널</td>
            <td style="padding:6px 12px">{channel}</td>
          </tr>
          <tr>
            <td style="padding:6px 12px;background:#f3f4f6;font-weight:bold">파일명</td>
            <td style="padding:6px 12px">{filename}</td>
          </tr>
        </table>
        <p>첨부된 Word 파일을 확인해 주세요.</p>
        <hr>
        <p style="color:#6b7280;font-size:12px">
          본 메일은 IBS 통역방송 시스템에서 자동 발송되었습니다.
        </p>
        </body></html>
        """

        results = []
        for recipient in recipients:
            success = send_email_with_attachment(
                to_email        = recipient["email"],
                to_name         = recipient["name"],
                subject         = subject,
                body            = body,
                attachment_data = docx_bytes,
                attachment_name = filename
            )
            results.append({
                "email":   recipient["email"],
                "success": success,
                "sent_at": datetime.now().isoformat()
            })
            _email_history.append({
                "to":      recipient["email"],
                "subject": subject,
                "file":    filename,
                "success": success,
                "sent_at": datetime.now().isoformat(),
                "channel": channel
            })

        success_cnt = sum(1 for r in results if r["success"])
        logger.info(f"이메일 전송: {success_cnt}/{len(results)}명 성공")
        return results

    except Exception as e:
        logger.error(f"이메일 전송 작업 실패: {e}")
        raise

# ────────────────────────────────────────────────────────────
# API 엔드포인트
# ────────────────────────────────────────────────────────────

@router.post("/test")
async def send_test_email():
    """테스트 이메일 전송"""
    try:
        subject = "[IBS] 이메일 연결 테스트"
        body = """
        <html><body style="font-family:Arial,sans-serif">
        <h2 style="color:#2563EB">✅ IBS 통역방송 이메일 연결 성공!</h2>
        <p>이메일 설정이 정상적으로 완료되었습니다.</p>
        <hr>
        <p style="color:#6b7280;font-size:12px">IBS 통역방송 시스템 자동 발송</p>
        </body></html>
        """
        success = send_email_with_attachment(
            to_email = SMTP_FROM,
            to_name  = "관리자",
            subject  = subject,
            body     = body
        )
        if success:
            return {"success": True, "message": f"{SMTP_FROM} 으로 테스트 이메일 전송 완료"}
        else:
            raise HTTPException(status_code=500, detail="이메일 전송 실패")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-transcript")
async def send_transcript(data: dict, background_tasks: BackgroundTasks):
    docx_path  = data.get("docx_path")
    channel    = data.get("channel", "english")
    title      = data.get("title",   "통역 방송")
    custom_recipients = data.get("recipients")

    if not docx_path:
        raise HTTPException(status_code=400, detail="docx_path 필수")

    recipients = custom_recipients or RECIPIENTS.get(channel, RECIPIENTS["english"])
    background_tasks.add_task(
        send_transcript_job, docx_path, recipients, channel, title
    )
    return {
        "success":    True,
        "message":    f"{len(recipients)}명에게 전송 시작",
        "recipients": [r["email"] for r in recipients],
        "file":       docx_path
    }

@router.post("/send-manual")
async def send_manual(data: dict, background_tasks: BackgroundTasks):
    docx_path = data.get("docx_path")
    to_email  = data.get("to_email")
    to_name   = data.get("to_name", "통역자")
    channel   = data.get("channel", "english")
    title     = data.get("title",   "통역 방송")

    if not docx_path or not to_email:
        raise HTTPException(status_code=400, detail="docx_path, to_email 필수")

    recipients = [{"name": to_name, "email": to_email}]
    background_tasks.add_task(
        send_transcript_job, docx_path, recipients, channel, title
    )
    return {"success": True, "message": f"{to_email}로 전송 시작", "file": docx_path}

@router.get("/recipients")
async def get_recipients():
    return {"success": True, "recipients": RECIPIENTS}

@router.get("/history")
async def get_history():
    return {"success": True, "history": _email_history[-50:][::-1]}

@router.get("/transcripts-today")
async def get_today_transcripts():
    try:
        s3    = get_s3()
        today = datetime.now().strftime("%Y%m%d")
        res   = s3.list_objects_v2(Bucket="transcripts", Prefix=today)
        files = []
        for obj in res.get("Contents", []):
            files.append({
                "path":          f"transcripts/{obj['Key']}",
                "name":          obj["Key"].split("/")[-1],
                "size_kb":       round(obj["Size"]/1024, 1),
                "last_modified": obj["LastModified"].isoformat(),
            })
        return {"success": True, "files": files, "date": today}
    except Exception as e:
        return {"success": False, "files": [], "error": str(e)}

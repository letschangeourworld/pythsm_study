from fastapi import APIRouter, Request
from loguru import logger

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/livekit")
async def livekit_webhook(request: Request):
    body = await request.json()
    logger.info(f"LiveKit Webhook: {body.get('event')}")
    return {"received": True}

@router.post("/alertmanager")
async def alertmanager_webhook(request: Request):
    body = await request.json()
    logger.warning(f"Alert: {body}")
    return {"received": True}

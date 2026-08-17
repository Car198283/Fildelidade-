import hashlib
import hmac
import json

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Company
from app.services.whatsapp_service import WhatsAppService

router = APIRouter(prefix="/integracoes/meta/whatsapp", tags=["WhatsApp Cloud API"])


@router.get("/webhook", response_class=PlainTextResponse)
def verify_webhook(
    mode: str = Query(..., alias="hub.mode"),
    challenge: str = Query(..., alias="hub.challenge"),
    verify_token: str = Query(..., alias="hub.verify_token"),
):
    configured = settings.meta_webhook_verify_token
    if not configured:
        raise HTTPException(status_code=503, detail="Webhook Meta nao configurado")
    if mode != "subscribe" or not hmac.compare_digest(verify_token, configured):
        raise HTTPException(status_code=403, detail="Verificacao Meta recusada")
    return challenge


@router.post("/webhook")
async def receive_webhook(request: Request, db: Session = Depends(get_db)):
    app_secret = settings.meta_app_secret
    if not app_secret:
        raise HTTPException(status_code=503, detail="Assinatura Meta nao configurada")
    raw = await request.body()
    received = request.headers.get("X-Hub-Signature-256", "")
    expected = "sha256=" + hmac.new(app_secret.encode(), raw, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(received, expected):
        raise HTTPException(status_code=401, detail="Assinatura Meta invalida")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Payload Meta invalido") from exc

    updated = 0
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            phone_number_id = value.get("metadata", {}).get("phone_number_id")
            if not phone_number_id:
                continue
            # tenant-scope: global - Phone Number ID unico resolve a empresa do webhook.
            company = db.query(Company).filter(Company.whatsapp_phone_number_id == str(phone_number_id), Company.ativo == True).first()
            if not company:
                continue
            for status_item in value.get("statuses", []):
                errors = status_item.get("errors") or []
                error_message = errors[0].get("title") or errors[0].get("message") if errors else None
                message = WhatsAppService.update_provider_status(
                    db, company.id, status_item.get("id"), status_item.get("status"), error_message
                )
                updated += int(message is not None)
    return {"success": True, "updated": updated}

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.schemas import N8nWhatsAppConsume, WhatsAppMessageStatusUpdate, WhatsAppQueueGenerate
from app.services.whatsapp_service import WhatsAppService
from app.utils.dependencies import get_effective_company_id, get_writable_company_id, require_admin_or_master, require_n8n_company

router = APIRouter(prefix="/integracoes/n8n", tags=["Integracoes n8n"])


def _message_to_dict(message):
    return {
        "id": message.id,
        "customer_id": message.customer_id,
        "tipo": message.tipo,
        "telefone": message.telefone,
        "cliente_nome": message.cliente_nome,
        "mensagem": message.mensagem,
        "status": message.status,
        "provider_message_id": message.provider_message_id,
        "erro": message.erro,
        "created_at": message.created_at,
        "sent_at": message.sent_at,
        "scheduled_at": message.scheduled_at,
        "attempts": message.attempts,
        "max_attempts": message.max_attempts,
        "next_attempt_at": message.next_attempt_at,
        "idempotency_key": message.idempotency_key,
    }


@router.post("/whatsapp/fila/gerar")
def gerar_fila_whatsapp(
    body: WhatsAppQueueGenerate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_master),
    company_id: int = Depends(get_writable_company_id),
    idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=8, max_length=255),
):
    """Gera mensagens pendentes para o n8n enviar por WhatsApp."""

    try:
        messages = WhatsAppService.generate_queue(
            db=db,
            company_id=company_id,
            tipo=body.tipo,
            template=body.mensagem_template,
            customer_id=body.customer_id,
            batch_key=idempotency_key,
            created_by_user_id=current_user.id,
            scheduled_at=body.scheduled_at,
            max_attempts=body.max_attempts,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Variavel invalida no template: {exc}",
        )

    return {
        "success": True,
        "total": len(messages),
        "data": [_message_to_dict(message) for message in messages],
    }


@router.get("/whatsapp/fila")
def listar_fila_whatsapp(
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_master),
    company_id: int = Depends(get_effective_company_id),
):
    messages = WhatsAppService.list_messages(db, company_id, status_filter, limit)
    return {"success": True, "total": len(messages), "data": [_message_to_dict(item) for item in messages]}


@router.post("/whatsapp/fila/consumir")
def consumir_fila_n8n(
    body: N8nWhatsAppConsume,
    db: Session = Depends(get_db),
    company_id: int = Depends(require_n8n_company),
):
    messages = WhatsAppService.claim_pending(db, company_id, body.limit)
    return {"success": True, "total": len(messages), "data": [_message_to_dict(item) for item in messages]}


@router.post("/whatsapp/fila/{message_id}/callback")
def callback_fila_n8n(
    message_id: int,
    body: WhatsAppMessageStatusUpdate,
    db: Session = Depends(get_db),
    company_id: int = Depends(require_n8n_company),
):
    message = WhatsAppService.update_status(db, company_id, message_id, body.status, body.provider_message_id, body.erro)
    if not message:
        raise HTTPException(status_code=404, detail="Mensagem nao encontrada")
    return {"success": True, "data": _message_to_dict(message)}


@router.get("/whatsapp/fila/pendentes")
def listar_pendentes_whatsapp(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_master),
    company_id: int = Depends(get_effective_company_id),
):
    """Lista mensagens pendentes para o n8n consumir."""

    messages = WhatsAppService.list_pending(db, company_id, limit)
    return {
        "success": True,
        "total": len(messages),
        "data": [_message_to_dict(message) for message in messages],
    }


@router.put("/whatsapp/fila/{message_id}/status")
def atualizar_status_whatsapp(
    message_id: int,
    body: WhatsAppMessageStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_master),
    company_id: int = Depends(get_writable_company_id),
):
    """Marca mensagem como enviada, erro, cancelada etc."""

    message = WhatsAppService.update_status(
        db=db,
        company_id=company_id,
        message_id=message_id,
        status=body.status,
        provider_message_id=body.provider_message_id,
        erro=body.erro,
    )
    if not message:
        raise HTTPException(status_code=404, detail="Mensagem nao encontrada")

    return {
        "success": True,
        "data": _message_to_dict(message),
    }

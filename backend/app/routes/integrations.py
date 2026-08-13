from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.schemas import WhatsAppMessageStatusUpdate, WhatsAppQueueGenerate
from app.services.whatsapp_service import WhatsAppService
from app.utils.dependencies import get_writable_company_id, require_admin_or_master

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
    }


@router.post("/whatsapp/fila/gerar")
def gerar_fila_whatsapp(
    body: WhatsAppQueueGenerate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_master),
    company_id: int = Depends(get_writable_company_id),
):
    """Gera mensagens pendentes para o n8n enviar por WhatsApp."""

    try:
        messages = WhatsAppService.generate_queue(
            db=db,
            company_id=company_id,
            tipo=body.tipo,
            template=body.mensagem_template,
            customer_id=body.customer_id,
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


@router.get("/whatsapp/fila/pendentes")
def listar_pendentes_whatsapp(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_master),
):
    """Lista mensagens pendentes para o n8n consumir."""

    messages = WhatsAppService.list_pending(db, current_user.company_id, limit)
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

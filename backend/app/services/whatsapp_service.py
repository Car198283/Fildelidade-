from datetime import datetime, timedelta
from hashlib import sha256

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models import Customer, WhatsAppMessage
from app.services.dashboard_service import DashboardService


class WhatsAppService:
    """Servico de fila de WhatsApp para o n8n consumir."""

    @staticmethod
    def _format_phone(phone: str) -> str:
        digits = "".join(ch for ch in str(phone or "") if ch.isdigit())
        if len(digits) in (10, 11):
            return f"55{digits}"
        return digits

    @staticmethod
    def _render_template(template: str, customer: Customer) -> str:
        return template.format(
            nome=customer.nome or "",
            telefone=customer.telefone or "",
            pontos=customer.pontos or 0,
        )

    @staticmethod
    def _eligible_customers(db: Session, company_id: int, tipo: str, customer_id: int = None) -> list[Customer]:
        query = db.query(Customer).filter(
            Customer.company_id == company_id,
            Customer.ativo == True,
            Customer.telefone != None,
        )

        if customer_id:
            return query.filter(Customer.id == customer_id).all()

        if tipo == "aniversario":
            ids = [
                item["id"]
                for item in DashboardService.get_aniversariantes(db, company_id, limit=500)
            ]
            return query.filter(Customer.id.in_(ids)).all() if ids else []

        if tipo == "premio":
            ids = [
                item["id"]
                for item in DashboardService.get_clientes_premiados_completo(db, company_id, limit=500)
            ]
            return query.filter(Customer.id.in_(ids)).all() if ids else []

        return query.all()

    @staticmethod
    def generate_queue(
        db: Session,
        company_id: int,
        tipo: str,
        template: str,
        customer_id: int = None,
        batch_key: str = None,
        created_by_user_id: int = None,
        scheduled_at: datetime = None,
        max_attempts: int = 3,
    ) -> list[WhatsAppMessage]:
        tipo = tipo.strip().lower()
        customers = WhatsAppService._eligible_customers(db, company_id, tipo, customer_id)
        messages = []

        for customer in customers:
            telefone = WhatsAppService._format_phone(customer.telefone)
            if not telefone:
                continue

            derived_key = sha256(f"{company_id}:{batch_key}:{customer.id}".encode()).hexdigest()
            existing = db.query(WhatsAppMessage).filter(
                WhatsAppMessage.company_id == company_id,
                WhatsAppMessage.idempotency_key == derived_key,
            ).first()
            if existing:
                messages.append(existing)
                continue
            message = WhatsAppMessage(
                company_id=company_id,
                customer_id=customer.id,
                tipo=tipo,
                telefone=telefone,
                cliente_nome=customer.nome,
                mensagem=WhatsAppService._render_template(template, customer),
                status="pendente",
                scheduled_at=scheduled_at,
                idempotency_key=derived_key,
                max_attempts=max_attempts,
                created_by_user_id=created_by_user_id,
                metadata_json={"batch_key": batch_key},
            )
            db.add(message)
            messages.append(message)

        db.commit()
        for message in messages:
            db.refresh(message)

        return messages

    @staticmethod
    def list_pending(db: Session, company_id: int, limit: int = 20) -> list[WhatsAppMessage]:
        now = datetime.utcnow()
        return db.query(WhatsAppMessage).filter(
            WhatsAppMessage.company_id == company_id,
            WhatsAppMessage.status == "pendente",
            (WhatsAppMessage.scheduled_at == None) | (WhatsAppMessage.scheduled_at <= now),
            (WhatsAppMessage.next_attempt_at == None) | (WhatsAppMessage.next_attempt_at <= now),
            WhatsAppMessage.attempts < WhatsAppMessage.max_attempts,
        ).order_by(WhatsAppMessage.created_at.asc()).limit(limit).all()

    @staticmethod
    def claim_pending(db: Session, company_id: int, limit: int = 20) -> list[WhatsAppMessage]:
        now = datetime.utcnow()
        stale_before = now - timedelta(minutes=10)
        stale_exhausted = db.query(WhatsAppMessage).filter(
            WhatsAppMessage.company_id == company_id,
            WhatsAppMessage.status == "processando",
            WhatsAppMessage.claimed_at <= stale_before,
            WhatsAppMessage.attempts >= WhatsAppMessage.max_attempts,
        ).all()
        for message in stale_exhausted:
            message.status = "erro"
            message.erro = message.erro or "Limite de tentativas excedido sem callback do n8n"

        query = db.query(WhatsAppMessage).filter(
            WhatsAppMessage.company_id == company_id,
            or_(
                WhatsAppMessage.status == "pendente",
                and_(WhatsAppMessage.status == "processando", WhatsAppMessage.claimed_at <= stale_before),
            ),
            (WhatsAppMessage.scheduled_at == None) | (WhatsAppMessage.scheduled_at <= now),
            (WhatsAppMessage.next_attempt_at == None) | (WhatsAppMessage.next_attempt_at <= now),
            WhatsAppMessage.attempts < WhatsAppMessage.max_attempts,
        ).order_by(WhatsAppMessage.created_at.asc()).limit(limit)
        if db.bind.dialect.name == "postgresql":
            query = query.with_for_update(skip_locked=True)
        messages = query.all()
        for message in messages:
            message.status = "processando"
            message.claimed_at = now
            message.last_attempt_at = now
            message.attempts += 1
        db.commit()
        for message in messages:
            db.refresh(message)
        return messages

    @staticmethod
    def list_messages(db: Session, company_id: int, status_filter: str = None, limit: int = 100):
        query = db.query(WhatsAppMessage).filter(WhatsAppMessage.company_id == company_id)
        if status_filter:
            query = query.filter(WhatsAppMessage.status == status_filter)
        return query.order_by(WhatsAppMessage.created_at.desc()).limit(limit).all()

    @staticmethod
    def update_status(
        db: Session,
        company_id: int,
        message_id: int,
        status: str,
        provider_message_id: str = None,
        erro: str = None,
    ) -> WhatsAppMessage:
        message = db.query(WhatsAppMessage).filter(
            WhatsAppMessage.id == message_id,
            WhatsAppMessage.company_id == company_id,
        ).first()
        if not message:
            return None

        if status == "erro" and message.attempts < message.max_attempts:
            message.status = "pendente"
            message.next_attempt_at = datetime.utcnow() + timedelta(minutes=2 ** max(message.attempts - 1, 0))
        else:
            message.status = status
            message.next_attempt_at = None
        message.provider_message_id = provider_message_id
        message.erro = erro
        if status in {"enviado", "entregue", "lido"}:
            message.sent_at = datetime.utcnow()

        db.commit()
        db.refresh(message)
        return message

from datetime import datetime

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
    ) -> list[WhatsAppMessage]:
        tipo = tipo.strip().lower()
        customers = WhatsAppService._eligible_customers(db, company_id, tipo, customer_id)
        messages = []

        for customer in customers:
            telefone = WhatsAppService._format_phone(customer.telefone)
            if not telefone:
                continue

            message = WhatsAppMessage(
                company_id=company_id,
                customer_id=customer.id,
                tipo=tipo,
                telefone=telefone,
                cliente_nome=customer.nome,
                mensagem=WhatsAppService._render_template(template, customer),
                status="pendente",
            )
            db.add(message)
            messages.append(message)

        db.commit()
        for message in messages:
            db.refresh(message)

        return messages

    @staticmethod
    def list_pending(db: Session, company_id: int, limit: int = 20) -> list[WhatsAppMessage]:
        return db.query(WhatsAppMessage).filter(
            WhatsAppMessage.company_id == company_id,
            WhatsAppMessage.status == "pendente",
        ).order_by(WhatsAppMessage.created_at.asc()).limit(limit).all()

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

        message.status = status
        message.provider_message_id = provider_message_id
        message.erro = erro
        if status == "enviado":
            message.sent_at = datetime.utcnow()

        db.commit()
        db.refresh(message)
        return message

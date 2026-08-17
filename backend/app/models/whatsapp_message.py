from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class WhatsAppMessage(Base, TimestampMixin):
    """Fila de mensagens para integracao com n8n/WhatsApp."""

    __tablename__ = "whatsapp_messages"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True, index=True)
    tipo = Column(String(50), nullable=False, index=True)
    telefone = Column(String(30), nullable=False, index=True)
    cliente_nome = Column(String(255), nullable=True)
    mensagem = Column(Text, nullable=False)
    status = Column(String(30), nullable=False, default="pendente", index=True)
    provider_message_id = Column(String(255), nullable=True)
    erro = Column(Text, nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    idempotency_key = Column(String(255), nullable=True)
    attempts = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=3)
    next_attempt_at = Column(DateTime, nullable=True)
    claimed_at = Column(DateTime, nullable=True)
    last_attempt_at = Column(DateTime, nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    metadata_json = Column(JSON, nullable=True)

    __table_args__ = (
        Index("idx_whatsapp_company_status", "company_id", "status"),
        Index("idx_whatsapp_customer", "customer_id"),
        UniqueConstraint("company_id", "idempotency_key", name="uq_whatsapp_company_idempotency"),
    )

    company = relationship("Company")
    customer = relationship("Customer")

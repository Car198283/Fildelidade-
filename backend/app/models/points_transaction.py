from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base, TimestampMixin

class PointsTransaction(Base, TimestampMixin):
    """Modelo de Transação de Pontos (Auditoria completa)"""
    __tablename__ = "points_transactions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    product_nome = Column(String(255), nullable=True)
    pontos = Column(Numeric(12, 2), nullable=False)  # Valor da transacao
    valor_compra = Column(Numeric(12, 2), nullable=True)
    tipo = Column(String(20), nullable=False)  # "entrada" ou "saida"
    descricao = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    origem = Column(String(50), nullable=False, default="api")
    motivo = Column(String(500), nullable=False)
    idempotency_key = Column(String(255), nullable=True)
    
    # Índices
    __table_args__ = (
        Index('idx_transaction_customer', 'customer_id'),
        Index('idx_transaction_company', 'company_id'),
        Index('idx_transaction_product', 'product_id'),
        Index('idx_transaction_created', 'created_at'),
        UniqueConstraint('company_id', 'idempotency_key', name='uq_points_company_idempotency'),
    )

    # Relacionamentos
    customer = relationship("Customer", back_populates="transactions")
    company = relationship("Company", back_populates="points_transactions")
    product = relationship("Product")

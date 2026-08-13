from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Index, Date, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, date
from app.models.base import Base, TimestampMixin

class Customer(Base, TimestampMixin):
    """Modelo de Cliente (com saldo de pontos e data de nascimento)"""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    telefone = Column(String(20), nullable=True, index=True)  # Index para busca rápida
    email = Column(String(255), nullable=True)
    data_nascimento = Column(Date, nullable=True)  # Para aniversariantes
    pontos = Column(Numeric(12, 2), default=0, nullable=False)  # Saldo atual
    ativo = Column(Boolean, default=True, nullable=False)  # Flag de atividade
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Rastreamento de progresso para premiação
    valor_gasto_atual = Column(Numeric(12, 2), default=0, nullable=False)  # Para promocao por valor
    quantidade_produtos_comprados = Column(Integer, default=0, nullable=False)  # Para promoção por quantidade
    meta_premiacao_valor = Column(Numeric(12, 2), nullable=True)  # Meta em Reais
    meta_premiacao_quantidade = Column(Integer, nullable=True)  # Meta em quantidade de produtos

    # Índices para queries rápidas
    __table_args__ = (
        Index('idx_customer_company', 'company_id'),
        Index('idx_customer_nome', 'nome'),
        Index('idx_customer_telefone', 'telefone'),
        Index('idx_customer_data_nascimento', 'data_nascimento'),
    )

    # Relacionamentos
    company = relationship("Company", back_populates="customers")
    transactions = relationship("PointsTransaction", back_populates="customer", cascade="all, delete-orphan")

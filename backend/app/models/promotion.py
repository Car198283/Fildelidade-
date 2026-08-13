from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Index, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base, TimestampMixin

class TipoPromocao(str, enum.Enum):
    """Tipos de promoção disponíveis"""
    QUANTIDADE = "quantidade"  # A cada X produtos, ganha Y pontos
    VALOR = "valor"  # A cada R$ X gasto, ganha Y pontos
    PERCENTUAL = "percentual"  # % do valor gasto em pontos
    PERSONALIZADA = "personalizada"  # Texto livre para regra personalizada

class PromotionConfig(Base, TimestampMixin):
    """Configuração de promoções por empresa"""
    __tablename__ = "promotion_configs"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Tipo de promoção
    tipo = Column(SQLEnum(TipoPromocao), nullable=False, default=TipoPromocao.QUANTIDADE)
    
    # Configurações por tipo:
    # QUANTIDADE: a cada X produtos comprados, ganha Y pontos
    quantidade_produtos = Column(Integer, nullable=True)  # Ex: 10 produtos
    pontos_por_quantidade = Column(Numeric(12, 2), nullable=True)  # Ex: 1 ponto
    
    # VALOR: a cada R$ X gasto, ganha Y pontos
    valor_gasto = Column(Numeric(12, 2), nullable=True)  # Ex: R$ 100.00
    pontos_por_valor = Column(Numeric(12, 2), nullable=True)  # Ex: 10 pontos
    
    # PERCENTUAL: % do valor em pontos
    percentual = Column(Numeric(5, 2), nullable=True)  # Ex: 5% = 5.0
    
    # Informações
    descricao = Column(String(500), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)
    
    # Índices
    __table_args__ = (
        Index('idx_promotion_company', 'company_id'),
    )
    
    # Relacionamentos
    company = relationship("Company", back_populates="promotion_configs")

    def __repr__(self):
        return f"<PromotionConfig tipo={self.tipo} company_id={self.company_id}>"

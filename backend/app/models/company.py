from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base, TimestampMixin

class Company(Base, TimestampMixin):
    """Modelo de Empresa"""
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    plano = Column(String(50), default="free")  # free, starter, pro, enterprise
    ativo = Column(Boolean, default=True)
    read_only = Column(Boolean, default=False, nullable=False)

    # Relacionamentos
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="company", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="company", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="company", cascade="all, delete-orphan")
    points_transactions = relationship("PointsTransaction", back_populates="company", cascade="all, delete-orphan")
    promotion_configs = relationship("PromotionConfig", back_populates="company", cascade="all, delete-orphan")  # NOVO

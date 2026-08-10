from sqlalchemy import Column, Integer, String, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class Category(Base, TimestampMixin):
    """Modelo de Categoria de Produtos"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)

    __table_args__ = (
        Index('idx_category_company', 'company_id'),
    )

    # Relacionamentos
    company = relationship("Company", back_populates="categories")
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")

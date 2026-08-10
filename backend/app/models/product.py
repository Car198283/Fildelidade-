from sqlalchemy import Column, Integer, String, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class Product(Base, TimestampMixin):
    """Modelo de Produto"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    preco = Column(Float, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)

    __table_args__ = (
        Index('idx_product_company', 'company_id'),
        Index('idx_product_category', 'categoria_id'),
    )

    # Relacionamentos
    company = relationship("Company", back_populates="products")
    category = relationship("Category", back_populates="products")

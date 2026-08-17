from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base, TimestampMixin

class User(Base, TimestampMixin):
    """Modelo de Usuário (Admin/Staff)"""
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('master', 'admin', 'operador_captura', 'observador')",
            name="ck_users_role",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    role = Column(String(50), default="admin")  # admin, staff
    ativo = Column(Boolean, default=True)

    # Relacionamentos
    company = relationship("Company", back_populates="users")

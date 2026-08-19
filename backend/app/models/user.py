from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Integer, JSON, String
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
    nome = Column(String(160), nullable=True)
    senha_hash = Column(String(255), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    role = Column(String(50), default="admin")  # admin, staff
    ativo = Column(Boolean, default=True)
    ultimo_acesso = Column(DateTime, nullable=True)
    exigir_troca_senha = Column(Boolean, default=False, nullable=False)
    excluido_em = Column(DateTime, nullable=True, index=True)

    # Relacionamentos
    company = relationship("Company", back_populates="users")


class UserAudit(Base, TimestampMixin):
    """Historico imutavel das alteracoes administrativas de usuarios."""
    __tablename__ = "user_audits"

    id = Column(Integer, primary_key=True)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    acao = Column(String(40), nullable=False)
    motivo = Column(String(500), nullable=False)
    detalhes = Column(JSON, nullable=True)

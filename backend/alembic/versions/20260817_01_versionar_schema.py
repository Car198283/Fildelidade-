"""Versiona o schema existente e adiciona auditoria/idempotencia."""
from alembic import op
import sqlalchemy as sa
from app.models import Base

revision = "20260817_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    if not sa.inspect(bind).has_table("points_transactions"):
        Base.metadata.create_all(bind=bind)
        return
    op.create_check_constraint(
        "ck_users_role", "users", "role IN ('master', 'admin', 'operador_captura', 'observador')"
    )
    op.add_column("points_transactions", sa.Column("user_id", sa.Integer(), nullable=True))
    op.add_column("points_transactions", sa.Column("origem", sa.String(50), nullable=True))
    op.add_column("points_transactions", sa.Column("motivo", sa.String(500), nullable=True))
    op.add_column("points_transactions", sa.Column("idempotency_key", sa.String(255), nullable=True))
    op.create_foreign_key("fk_points_transactions_user", "points_transactions", "users", ["user_id"], ["id"])
    op.create_index("ix_points_transactions_user_id", "points_transactions", ["user_id"])
    op.create_unique_constraint(
        "uq_points_company_idempotency", "points_transactions", ["company_id", "idempotency_key"]
    )


def downgrade():
    op.drop_constraint("ck_users_role", "users", type_="check")
    op.drop_constraint("uq_points_company_idempotency", "points_transactions", type_="unique")
    op.drop_index("ix_points_transactions_user_id", table_name="points_transactions")
    op.drop_constraint("fk_points_transactions_user", "points_transactions", type_="foreignkey")
    for column in ("idempotency_key", "motivo", "origem", "user_id"):
        op.drop_column("points_transactions", column)

"""Adiciona dados gerenciais e auditoria de usuarios."""
from alembic import op
import sqlalchemy as sa

revision = "20260817_04"
down_revision = "20260817_03"
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    existing = {column["name"] for column in inspector.get_columns("users")}
    fields = [
        ("nome", sa.String(160), True, None),
        ("ultimo_acesso", sa.DateTime(), True, None),
        ("exigir_troca_senha", sa.Boolean(), False, sa.false()),
    ]
    for name, column_type, nullable, default in fields:
        if name not in existing:
            op.add_column("users", sa.Column(name, column_type, nullable=nullable, server_default=default))

    if not inspector.has_table("user_audits"):
        op.create_table(
            "user_audits",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("target_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
            sa.Column("acao", sa.String(40), nullable=False),
            sa.Column("motivo", sa.String(500), nullable=False),
            sa.Column("detalhes", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_user_audits_target_user_id", "user_audits", ["target_user_id"])
        op.create_index("ix_user_audits_actor_user_id", "user_audits", ["actor_user_id"])
        op.create_index("ix_user_audits_company_id", "user_audits", ["company_id"])


def downgrade():
    op.drop_table("user_audits")
    for name in ("exigir_troca_senha", "ultimo_acesso", "nome"):
        op.drop_column("users", name)

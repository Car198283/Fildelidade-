"""Adiciona ciclo de vida, regras e auditoria de promocoes."""
from alembic import op
import sqlalchemy as sa

revision = "20260817_03"
down_revision = "20260817_02"
branch_labels = None
depends_on = None


def upgrade():
    fields = [
        ("nome", sa.String(120), True, None),
        ("data_inicio", sa.DateTime(), True, None),
        ("data_fim", sa.DateTime(), True, None),
        ("acumulavel", sa.Boolean(), False, sa.true()),
        ("prioridade", sa.Integer(), False, "0"),
        ("limite_por_cliente", sa.Integer(), True, None),
        ("limite_total", sa.Integer(), True, None),
        ("valor_minimo_compra", sa.Numeric(12, 2), True, None),
        ("recompensa_tipo", sa.String(30), False, "'pontos'"),
        ("recompensa_valor", sa.Numeric(12, 2), True, None),
        ("condicao_campo", sa.String(50), True, None),
        ("condicao_operador", sa.String(20), True, None),
        ("condicao_valor", sa.Numeric(12, 2), True, None),
        ("produtos_elegiveis", sa.JSON(), True, None),
        ("categorias_elegiveis", sa.JSON(), True, None),
        ("motivo_alteracao", sa.String(500), True, None),
    ]
    existing = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("promotion_configs")}
    for name, column_type, nullable, default in fields:
        if name not in existing:
            op.add_column("promotion_configs", sa.Column(name, column_type, nullable=nullable, server_default=default))

    inspector = sa.inspect(op.get_bind())
    if not inspector.has_table("promotion_audits"):
        op.create_table(
            "promotion_audits",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("promotion_id", sa.Integer(), sa.ForeignKey("promotion_configs.id"), nullable=False),
            sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("acao", sa.String(30), nullable=False),
            sa.Column("motivo", sa.String(500), nullable=False),
            sa.Column("antes", sa.JSON(), nullable=True),
            sa.Column("depois", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_promotion_audits_promotion_id", "promotion_audits", ["promotion_id"])
        op.create_index("ix_promotion_audits_company_id", "promotion_audits", ["company_id"])
        op.create_index("ix_promotion_audits_user_id", "promotion_audits", ["user_id"])


def downgrade():
    op.drop_table("promotion_audits")
    for name in ("motivo_alteracao", "categorias_elegiveis", "produtos_elegiveis", "condicao_valor", "condicao_operador", "condicao_campo", "recompensa_valor", "recompensa_tipo", "valor_minimo_compra", "limite_total", "limite_por_cliente", "prioridade", "acumulavel", "data_fim", "data_inicio", "nome"):
        op.drop_column("promotion_configs", name)

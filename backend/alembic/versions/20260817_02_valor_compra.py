"""Adiciona valor da compra para indicadores financeiros."""
from alembic import op
import sqlalchemy as sa

revision = "20260817_02"
down_revision = "20260817_01"
branch_labels = None
depends_on = None


def upgrade():
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("points_transactions")}
    if "valor_compra" not in columns:
        op.add_column("points_transactions", sa.Column("valor_compra", sa.Numeric(12, 2), nullable=True))


def downgrade():
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("points_transactions")}
    if "valor_compra" in columns:
        op.drop_column("points_transactions", "valor_compra")

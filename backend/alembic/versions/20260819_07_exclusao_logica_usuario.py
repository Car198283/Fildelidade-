"""Adiciona exclusao logica de usuarios preservando o historico."""
from alembic import op
import sqlalchemy as sa

revision = "20260819_07"
down_revision = "20260817_06"
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    existing = {column["name"] for column in inspector.get_columns("users")}
    if "excluido_em" not in existing:
        op.add_column("users", sa.Column("excluido_em", sa.DateTime(), nullable=True))
        op.create_index("ix_users_excluido_em", "users", ["excluido_em"])


def downgrade():
    op.drop_index("ix_users_excluido_em", table_name="users")
    op.drop_column("users", "excluido_em")

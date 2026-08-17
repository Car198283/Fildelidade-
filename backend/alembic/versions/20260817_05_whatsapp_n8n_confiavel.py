"""Adiciona idempotencia, tentativas e claim seguro a fila WhatsApp."""
from alembic import op
import sqlalchemy as sa

revision = "20260817_05"
down_revision = "20260817_04"
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    existing = {column["name"] for column in inspector.get_columns("whatsapp_messages")}
    fields = [
        ("idempotency_key", sa.String(255), True, None),
        ("attempts", sa.Integer(), False, "0"),
        ("max_attempts", sa.Integer(), False, "3"),
        ("next_attempt_at", sa.DateTime(), True, None),
        ("claimed_at", sa.DateTime(), True, None),
        ("last_attempt_at", sa.DateTime(), True, None),
        ("created_by_user_id", sa.Integer(), True, None),
        ("metadata_json", sa.JSON(), True, None),
    ]
    for name, kind, nullable, default in fields:
        if name not in existing:
            op.add_column("whatsapp_messages", sa.Column(name, kind, nullable=nullable, server_default=default))
    inspector = sa.inspect(op.get_bind())
    foreign_keys = {fk.get("name") for fk in inspector.get_foreign_keys("whatsapp_messages")}
    unique_names = {item.get("name") for item in inspector.get_unique_constraints("whatsapp_messages")}
    needs_fk = "fk_whatsapp_created_by_user" not in foreign_keys
    needs_unique = "uq_whatsapp_company_idempotency" not in unique_names
    if op.get_bind().dialect.name == "sqlite":
        with op.batch_alter_table("whatsapp_messages") as batch:
            if needs_fk:
                batch.create_foreign_key("fk_whatsapp_created_by_user", "users", ["created_by_user_id"], ["id"])
            if needs_unique:
                batch.create_unique_constraint("uq_whatsapp_company_idempotency", ["company_id", "idempotency_key"])
    else:
        if needs_fk:
            op.create_foreign_key("fk_whatsapp_created_by_user", "whatsapp_messages", "users", ["created_by_user_id"], ["id"])
        if needs_unique:
            op.create_unique_constraint("uq_whatsapp_company_idempotency", "whatsapp_messages", ["company_id", "idempotency_key"])


def downgrade():
    op.drop_constraint("uq_whatsapp_company_idempotency", "whatsapp_messages", type_="unique")
    op.drop_constraint("fk_whatsapp_created_by_user", "whatsapp_messages", type_="foreignkey")
    for name in ("metadata_json", "created_by_user_id", "last_attempt_at", "claimed_at", "next_attempt_at", "max_attempts", "attempts", "idempotency_key"):
        op.drop_column("whatsapp_messages", name)

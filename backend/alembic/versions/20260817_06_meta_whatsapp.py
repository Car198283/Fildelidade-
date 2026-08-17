"""Mapeia identificadores WhatsApp Cloud API por empresa."""
from alembic import op
import sqlalchemy as sa

revision = "20260817_06"
down_revision = "20260817_05"
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    existing = {column["name"] for column in inspector.get_columns("companies")}
    if "whatsapp_phone_number_id" not in existing:
        op.add_column("companies", sa.Column("whatsapp_phone_number_id", sa.String(80), nullable=True))
    if "whatsapp_business_account_id" not in existing:
        op.add_column("companies", sa.Column("whatsapp_business_account_id", sa.String(80), nullable=True))
    uniques = {item.get("name") for item in sa.inspect(op.get_bind()).get_unique_constraints("companies")}
    if "uq_companies_whatsapp_phone_number_id" not in uniques:
        if op.get_bind().dialect.name == "sqlite":
            with op.batch_alter_table("companies") as batch:
                batch.create_unique_constraint("uq_companies_whatsapp_phone_number_id", ["whatsapp_phone_number_id"])
        else:
            op.create_unique_constraint("uq_companies_whatsapp_phone_number_id", "companies", ["whatsapp_phone_number_id"])


def downgrade():
    op.drop_constraint("uq_companies_whatsapp_phone_number_id", "companies", type_="unique")
    op.drop_column("companies", "whatsapp_business_account_id")
    op.drop_column("companies", "whatsapp_phone_number_id")

"""auditoria de exportacao de relatorios master

Revision ID: 20260820_08
Revises: 20260819_07
"""
from alembic import op
import sqlalchemy as sa

revision = "20260820_08"
down_revision = "20260819_07"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "report_export_audits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=True),
        sa.Column("report_type", sa.String(length=40), nullable=False),
        sa.Column("export_format", sa.String(length=10), nullable=False),
        sa.Column("filters", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_report_export_audits_user_id", "report_export_audits", ["user_id"])
    op.create_index("ix_report_export_audits_company_id", "report_export_audits", ["company_id"])
    op.create_index("ix_report_export_audits_report_type", "report_export_audits", ["report_type"])


def downgrade():
    op.drop_index("ix_report_export_audits_report_type", table_name="report_export_audits")
    op.drop_index("ix_report_export_audits_company_id", table_name="report_export_audits")
    op.drop_index("ix_report_export_audits_user_id", table_name="report_export_audits")
    op.drop_table("report_export_audits")

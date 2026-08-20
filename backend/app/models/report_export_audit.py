from sqlalchemy import Column, ForeignKey, Integer, JSON, String

from app.models.base import Base, TimestampMixin


class ReportExportAudit(Base, TimestampMixin):
    __tablename__ = "report_export_audits"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    report_type = Column(String(40), nullable=False, index=True)
    export_format = Column(String(10), nullable=False)
    filters = Column(JSON, nullable=True)

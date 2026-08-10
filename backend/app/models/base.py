from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import Column, DateTime

Base = declarative_base()

class TimestampMixin:
    """Mixin para adicionar timestamps"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

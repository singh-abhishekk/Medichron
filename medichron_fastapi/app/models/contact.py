"""
Contact form database model.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from app.core.database import Base


class Contact(Base):
    """Contact form submission model."""

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_resolved = Column(Integer, default=0)  # 0 = pending, 1 = resolved

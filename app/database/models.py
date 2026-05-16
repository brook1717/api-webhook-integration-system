import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, JSON, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.db import Base


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    api_requests = relationship("APIRequestLog", back_populates="webhook_event")


class APIRequestLog(Base):
    __tablename__ = "api_request_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    webhook_event_id = Column(UUID(as_uuid=True), ForeignKey("webhook_events.id"), nullable=False)
    target_service = Column(String, nullable=False)
    request_body = Column(JSON, nullable=True)
    response_status_code = Column(Integer, nullable=True)
    response_body = Column(JSON, nullable=True)
    success = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    webhook_event = relationship("WebhookEvent", back_populates="api_requests")

# models/event.py
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from db import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    date_time: Mapped[datetime] = mapped_column()
    event_type: Mapped[str] = mapped_column()
    event_state: Mapped[str] = mapped_column(nullable=True)
    event_description: Mapped[str] = mapped_column(nullable=True)
    device_id: Mapped[str] = mapped_column(nullable=True)
    employee_name: Mapped[str] = mapped_column(nullable=True)
    employee_no: Mapped[str] = mapped_column(nullable=True)
    major_event_type: Mapped[int] = mapped_column()
    sub_event_type: Mapped[int] = mapped_column()
    current_verify_mode: Mapped[str] = mapped_column(nullable=True)
    attendance_status: Mapped[str] = mapped_column(nullable=True)
    face_rect: Mapped[dict] = mapped_column(JSONB, nullable=True)
    picture_url: Mapped[str] = mapped_column(nullable=True)

# models/event.py
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from db import Base



class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    date_time: Mapped[datetime] = mapped_column()
    event_type: Mapped[str] = mapped_column()
    event_state: Mapped[str] = mapped_column()
    event_description: Mapped[str] = mapped_column()
    device_id: Mapped[str] = mapped_column()
    employee_name: Mapped[str] = mapped_column()
    employee_no: Mapped[str] = mapped_column()
    major_event_type: Mapped[int] = mapped_column()
    sub_event_type: Mapped[int] = mapped_column()
    current_verify_mode: Mapped[str] = mapped_column(nullable=True)
    attendance_status: Mapped[str] = mapped_column()
    label: Mapped[str] = mapped_column(String(255), nullable=True)
    face_rect: Mapped[dict] = mapped_column(JSONB, nullable=True)
    picture_url: Mapped[str] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc), onupdate=datetime.now(datetime.timezone.utc), nullable=False)

    def __repr__(self):
        return f"<Event(id={self.id}, date_time={self.date_time}, event_type={self.event_type}, device_id={self.device_id})>"
    def to_dict(self):
        return {
            "id": self.id,
            "date_time": self.date_time.isoformat(),
            "event_type": self.event_type,
            "event_state": self.event_state,
            "event_description": self.event_description,
            "device_id": self.device_id,
            "employee_name": self.employee_name,
            "employee_no": self.employee_no,
            "major_event_type": self.major_event_type,
            "sub_event_type": self.sub_event_type,
            "current_verify_mode": self.current_verify_mode,
            "attendance_status": self.attendance_status,
            "face_rect": self.face_rect,
            "picture_url": self.picture_url,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    def __str__(self):
        return f"Event(id={self.id}, date_time={self.date_time}, event_type={self.event_type}, device_id={self.device_id}, employee_name={self.employee_name})"

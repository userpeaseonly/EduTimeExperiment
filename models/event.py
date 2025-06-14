from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.types import DateTime
from sqlalchemy.ext.mutable import MutableDict

from enum import Enum
from typing import Optional
from datetime import datetime, timezone

from db import Base



class PersonPurpose(str, Enum):
    ATTENDANCE = "att"
    INFORMATION = "info"


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Common event fields
    date_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    active_post_count: Mapped[int]
    event_type: Mapped[str] = mapped_column()
    event_state: Mapped[str]
    event_description: Mapped[str]
    device_id: Mapped[str] = mapped_column(index=True)

    # Access controller related (nullable if not applicable)
    major_event: Mapped[int] = mapped_column()
    minor_event: Mapped[int] = mapped_column()
    serial_no: Mapped[Optional[int]] = mapped_column(default=None)
    verify_no: Mapped[Optional[int]] = mapped_column(default=None)
    person_id: Mapped[Optional[str]] = mapped_column(default=None, index=True)
    purpose: Mapped[Optional[PersonPurpose]] = mapped_column(PgEnum(PersonPurpose, name="person_purpose_enum"), default=None)
    zone_type: Mapped[Optional[int]] = mapped_column(default=None)
    swipe_card_type: Mapped[Optional[int]] = mapped_column(default=None)
    card_no: Mapped[Optional[str]] = mapped_column(default=None)
    card_type: Mapped[Optional[int]] = mapped_column(default=None)
    user_type: Mapped[Optional[str]] = mapped_column(default=None)
    current_verify_mode: Mapped[Optional[str]] = mapped_column(default=None)
    current_event: Mapped[Optional[bool]] = mapped_column(default=None)
    front_serial_no: Mapped[Optional[int]] = mapped_column(default=None)
    attendance_status: Mapped[Optional[str]] = mapped_column(default=None, index=True)
    pictures_number: Mapped[Optional[int]] = mapped_column(default=None)
    mask: Mapped[Optional[str]] = mapped_column(default=None)

    # Optional structured metadata (can store raw nested values)
    event_metadata: Mapped[Optional[dict]] = mapped_column(MutableDict.as_mutable(JSONB), default=None)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    def is_attendance_event(self) -> bool:
        return (
            self.attendance_status is not None and
            self.purpose == PersonPurpose.ATTENDANCE
        )


class Heartbeat(Base):
    __tablename__ = "heartbeats"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    date_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    active_post_count: Mapped[int]
    event_type: Mapped[str] = mapped_column(default="heartBeat")
    event_state: Mapped[str]
    event_description: Mapped[str]
    device_id: Mapped[str] = mapped_column(index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
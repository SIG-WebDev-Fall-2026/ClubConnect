from datetime import time

from sqlalchemy import ForeignKey, Identity, String, Text, Time, false
from sqlalchemy.orm import Mapped, mapped_column

from main.extensions import db  # or wherever your `db = SQLAlchemy()` lives


class User(db.Model):
    __tablename__ = "users"

    user_id: Mapped[int]        = mapped_column(Identity(always=False), primary_key=True)
    username: Mapped[str]       = mapped_column(String(255), nullable=False, unique=True)
    operator: Mapped[bool]      = mapped_column(nullable=False, server_default=false())
    password: Mapped[str]       = mapped_column(String(255), nullable=False)
    description: Mapped[str]    = mapped_column(Text, nullable=True)


class Club(db.Model):
    __tablename__ = "clubs"

    club_id: Mapped[int]            = mapped_column(Identity(always=False), primary_key=True)
    club_name: Mapped[str]          = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class ClubRegularMeeting(db.Model):
    __tablename__ = "club_regular_meetings"

    meeting_id: Mapped[int]             = mapped_column(Identity(always=False), primary_key=True)
    club_id: Mapped[int]                = mapped_column(ForeignKey("clubs.club_id", ondelete="CASCADE"), nullable=False)
    start_time: Mapped[time]            = mapped_column(Time, nullable=False)
    end_time: Mapped[time]              = mapped_column(Time, nullable=False)
    day: Mapped[str]                    = mapped_column(String(20), nullable=False)
    meeting_interval: Mapped[str | None] = mapped_column(String(50), nullable=True)

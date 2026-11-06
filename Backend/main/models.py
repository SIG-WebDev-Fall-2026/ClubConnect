import datetime
from sqlalchemy import Identity, Time, Date, ForeignKey ,String, Text, false
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

class ClubEvents(db.Model):
    __tablename__ = "club_events"

    event_id: Mapped[int]               = mapped_column(Identity(always=False), primary_key=True)
    club_id: Mapped[int]                = mapped_column(ForeignKey("clubs.club_id", ondelete="CASCADE"), nullable=False)
    start_time: Mapped[datetime.time]   = mapped_column(Time, nullable=False)
    end_time: Mapped[datetime.time]     = mapped_column(Time, nullable=False)
    date: Mapped[datetime.date]         = mapped_column(Date, nullable=False)
    description: Mapped[str | None]     = mapped_column(Text, nullable=True)

    def to_dict(self):
        return {
            "event_id": self.event_id,
            "club_id": self.club_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "date": self.date.isoformat(),
            "description": self.description,
        }
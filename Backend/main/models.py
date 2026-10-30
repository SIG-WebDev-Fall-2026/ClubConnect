from sqlalchemy import Identity, String, Text, false
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

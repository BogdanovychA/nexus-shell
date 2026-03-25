# -*- coding: utf-8 -*-

from typing import List, Optional

from sqlalchemy import BigInteger, Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[Optional[str]] = mapped_column(String(255))
    first_name: Mapped[Optional[str]] = mapped_column(String(255))
    last_name: Mapped[Optional[str]] = mapped_column(String(255))
    is_premium: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    is_bot: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    language_code: Mapped[Optional[str]] = mapped_column(String(10))

    ai_settings: Mapped[List["AISettingORM"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class AISettingORM(Base):
    __tablename__ = "ai_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))

    model_name: Mapped[str] = mapped_column(String(50), index=True)

    prompt: Mapped[Optional[str]] = mapped_column(Text)
    token: Mapped[Optional[str]] = mapped_column(Text)

    user: Mapped["UserORM"] = relationship(back_populates="ai_settings")

    __table_args__ = (
        UniqueConstraint('user_id', 'model_name', name='idx_user_model_unique'),
    )

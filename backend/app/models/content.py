"""Curriculum tables, seeded from the shared content manifest.

Invariant: every module has exactly two learner-facing pages (position 1 and 2).
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, uuid_pk


class Module(Base, TimestampMixin):
    __tablename__ = "modules"

    id: Mapped[uuid.UUID] = uuid_pk()
    key: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    subtitle: Mapped[str] = mapped_column(String(400), nullable=False, default="")
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    accent: Mapped[str] = mapped_column(String(32), nullable=False, default="blue")
    content_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    pages: Mapped[list["ModulePage"]] = relationship(
        back_populates="module",
        cascade="all, delete-orphan",
        order_by="ModulePage.position",
        lazy="selectin",
    )

    __table_args__ = (UniqueConstraint("position", name="uq_modules_position"),)


class ModulePage(Base, TimestampMixin):
    __tablename__ = "module_pages"

    id: Mapped[uuid.UUID] = uuid_pk()
    module_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("modules.id", ondelete="CASCADE"), nullable=False
    )
    key: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    module_key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    kicker: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    kind: Mapped[str] = mapped_column(String(20), nullable=False)
    objectives: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    required_sections: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=15)
    content_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    module: Mapped[Module] = relationship(back_populates="pages")
    questions: Mapped[list["Question"]] = relationship(
        back_populates="page",
        cascade="all, delete-orphan",
        order_by="Question.position",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("module_id", "position", name="uq_module_pages_module_id_position"),
        CheckConstraint("position in (1, 2)", name="module_pages_exactly_two"),
    )


class Question(Base, TimestampMixin):
    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = uuid_pk()
    page_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("module_pages.id", ondelete="CASCADE"), nullable=False
    )
    key: Mapped[str] = mapped_column(String(96), nullable=False, unique=True)
    module_key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    page_key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    # Options, correctness rules, scale bounds, and per-option feedback.
    spec: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_graded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    page: Mapped[ModulePage] = relationship(back_populates="questions")

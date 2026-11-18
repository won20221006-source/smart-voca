#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - 단어장·단어·학습 기록 테이블 정의 (REQ-001~015, NFR-002, NFR-009)
# 파일 위치: src/models/entities.py

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.database import Base


class Wordbook(Base):
    """단어장. 삭제하면 소속 단어와 학습 기록이 함께 삭제된다. (REQ-004, NFR-009)"""

    __tablename__ = "wordbooks"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    words: Mapped[List["Word"]] = relationship(
        back_populates="wordbook",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Word.id",
    )


class Word(Base):
    """단어. 복습 상태(review_stage, next_review_date)를 함께 가진다. (REQ-005~009, REQ-016)"""

    __tablename__ = "words"

    id: Mapped[int] = mapped_column(primary_key=True)
    wordbook_id: Mapped[int] = mapped_column(
        ForeignKey("wordbooks.id", ondelete="CASCADE"), index=True
    )
    word: Mapped[str] = mapped_column(String(100))
    meaning: Mapped[str] = mapped_column(String(200))
    example: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    review_stage: Mapped[int] = mapped_column(default=0)
    next_review_date: Mapped[date] = mapped_column(Date, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    wordbook: Mapped[Wordbook] = relationship(back_populates="words")
    records: Mapped[List["StudyRecord"]] = relationship(
        back_populates="word",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class StudyRecord(Base):
    """학습 이력 한 건. 정답 여부와 시각을 남긴다. (REQ-013, REQ-015)"""

    __tablename__ = "study_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    word_id: Mapped[int] = mapped_column(
        ForeignKey("words.id", ondelete="CASCADE"), index=True
    )
    is_correct: Mapped[bool] = mapped_column(Boolean)
    studied_at: Mapped[datetime] = mapped_column(DateTime)
    studied_on: Mapped[date] = mapped_column(Date, index=True)

    word: Mapped[Word] = relationship(back_populates="records")

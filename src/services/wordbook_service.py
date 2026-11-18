#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - 단어장 생성·조회·이름 수정·삭제 업무 로직 (F1.1~F1.4)
# 파일 위치: src/services/wordbook_service.py

from __future__ import annotations

from typing import List, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.core.errors import NotFoundError
from src.core.validation import WORDBOOK_NAME_MAX_LENGTH, clean_required_text
from src.models.entities import Wordbook, Word


def create_wordbook(session: Session, name: str) -> Wordbook:
    """단어장을 만든다. 이름은 1~50자. (REQ-001)"""
    cleaned_name = clean_required_text(name, "단어장 이름", WORDBOOK_NAME_MAX_LENGTH)
    wordbook = Wordbook(name=cleaned_name)
    session.add(wordbook)
    session.commit()
    return wordbook


def list_wordbooks_with_counts(session: Session) -> List[Tuple[Wordbook, int]]:
    """단어장 목록과 각 단어장의 단어 수를 돌려준다. (REQ-002)"""
    statement = (
        select(Wordbook, func.count(Word.id))
        .outerjoin(Word, Word.wordbook_id == Wordbook.id)
        .group_by(Wordbook.id)
        .order_by(Wordbook.id)
    )
    return [(wordbook, count) for wordbook, count in session.execute(statement).all()]


def get_wordbook(session: Session, wordbook_id: int) -> Wordbook:
    """단어장을 찾는다. 없으면 NotFoundError."""
    wordbook = session.get(Wordbook, wordbook_id)
    if wordbook is None:
        raise NotFoundError("단어장을 찾을 수 없습니다.")
    return wordbook


def rename_wordbook(session: Session, wordbook_id: int, name: str) -> Wordbook:
    """단어장 이름을 바꾼다. (REQ-003)"""
    wordbook = get_wordbook(session, wordbook_id)
    wordbook.name = clean_required_text(name, "단어장 이름", WORDBOOK_NAME_MAX_LENGTH)
    session.commit()
    return wordbook


def delete_wordbook(session: Session, wordbook_id: int) -> None:
    """단어장과 소속 단어·학습 기록을 함께 삭제한다. (REQ-004, NFR-009)"""
    wordbook = get_wordbook(session, wordbook_id)
    session.delete(wordbook)
    session.commit()

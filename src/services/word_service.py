#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - 단어 추가·예문·조회·수정·삭제와 중복 검사 업무 로직 (F2.1~F2.6)
# 파일 위치: src/services/word_service.py

from __future__ import annotations

from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.errors import DuplicateWordError, NotFoundError
from src.core.scheduler import create_initial_state
from src.core.validation import (
    MEANING_MAX_LENGTH,
    WORD_MAX_LENGTH,
    clean_optional_text,
    clean_required_text,
    normalize_word_key,
)
from src.models.entities import Word
from src.services.wordbook_service import get_wordbook


def list_words(session: Session, wordbook_id: int) -> List[Word]:
    """단어장의 단어 목록을 추가 순서대로 돌려준다. (REQ-007)"""
    get_wordbook(session, wordbook_id)
    statement = select(Word).where(Word.wordbook_id == wordbook_id).order_by(Word.id)
    return list(session.scalars(statement).all())


def get_word(session: Session, word_id: int) -> Word:
    """단어를 찾는다. 없으면 NotFoundError."""
    word = session.get(Word, word_id)
    if word is None:
        raise NotFoundError("단어를 찾을 수 없습니다.")
    return word


def ensure_not_duplicate(
    session: Session,
    wordbook_id: int,
    word_text: str,
    exclude_word_id: Optional[int] = None,
) -> None:
    """같은 단어장 안에 같은 단어(대소문자·공백 무시)가 있으면 DuplicateWordError. (REQ-010)"""
    target_key = normalize_word_key(word_text)
    for existing in list_words(session, wordbook_id):
        if existing.id == exclude_word_id:
            continue
        if normalize_word_key(existing.word) == target_key:
            raise DuplicateWordError()


def add_word(
    session: Session,
    wordbook_id: int,
    word_text: str,
    meaning: str,
    example: Optional[str],
    today: date,
) -> Word:
    """단어를 추가한다. 추가한 날이 첫 복습일이다 (가정, 요구사항 §5 확인 필요). (REQ-005, REQ-006)"""
    get_wordbook(session, wordbook_id)
    cleaned_word = clean_required_text(word_text, "단어", WORD_MAX_LENGTH)
    cleaned_meaning = clean_required_text(meaning, "뜻", MEANING_MAX_LENGTH)
    cleaned_example = clean_optional_text(example)
    ensure_not_duplicate(session, wordbook_id, cleaned_word)

    initial_state = create_initial_state(today)
    word = Word(
        wordbook_id=wordbook_id,
        word=cleaned_word,
        meaning=cleaned_meaning,
        example=cleaned_example,
        review_stage=initial_state.stage,
        next_review_date=initial_state.next_review_date,
    )
    session.add(word)
    session.commit()
    return word


def update_word(
    session: Session,
    word_id: int,
    word_text: str,
    meaning: str,
    example: Optional[str],
) -> Word:
    """단어·뜻·예문을 수정한다. 자기 자신은 중복 검사에서 제외한다. (REQ-008, REQ-010)"""
    word = get_word(session, word_id)
    cleaned_word = clean_required_text(word_text, "단어", WORD_MAX_LENGTH)
    cleaned_meaning = clean_required_text(meaning, "뜻", MEANING_MAX_LENGTH)
    ensure_not_duplicate(session, word.wordbook_id, cleaned_word, exclude_word_id=word.id)

    word.word = cleaned_word
    word.meaning = cleaned_meaning
    word.example = clean_optional_text(example)
    session.commit()
    return word


def delete_word(session: Session, word_id: int) -> int:
    """단어와 학습 기록을 삭제하고, 소속 단어장 id를 돌려준다. (REQ-009)"""
    word = get_word(session, word_id)
    wordbook_id = word.wordbook_id
    session.delete(word)
    session.commit()
    return wordbook_id

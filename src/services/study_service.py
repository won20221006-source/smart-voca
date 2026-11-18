#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - 학습 세션 대상 구성과 정답/오답 기록·복습일 갱신 (F3.1, F3.3, F3.4, F4.4)
# 파일 위치: src/services/study_service.py

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.clock import today_local
from src.core.scheduler import ReviewScheduler, ReviewState, create_default_scheduler
from src.models.entities import StudyRecord, Word
from src.services.word_service import get_word


def build_study_queue(session: Session, wordbook_id: int) -> List[int]:
    """단어장의 전체 단어 id를 순서대로 돌려준다. 학습 세션의 대상이 된다. (REQ-011)"""
    statement = select(Word.id).where(Word.wordbook_id == wordbook_id).order_by(Word.id)
    return list(session.scalars(statement).all())


def record_answer(
    session: Session,
    word_id: int,
    is_correct: bool,
    now: datetime,
    scheduler: Optional[ReviewScheduler] = None,
) -> Word:
    """정답/오답을 학습 기록에 남기고, 단어의 다음 복습일을 갱신한다. (REQ-013, REQ-015, REQ-016)"""
    word = get_word(session, word_id)
    calculator = scheduler or create_default_scheduler()
    next_state = calculator.calculate(
        ReviewState(stage=word.review_stage, next_review_date=word.next_review_date),
        is_correct=is_correct,
        today=today_local(now),
    )
    word.review_stage = next_state.stage
    word.next_review_date = next_state.next_review_date

    session.add(
        StudyRecord(
            word_id=word.id,
            is_correct=is_correct,
            studied_at=now,
            studied_on=today_local(now),
        )
    )
    session.commit()
    return word

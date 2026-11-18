#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - DB 학습 기록을 통계 순수 함수에 넘기는 통계 업무 로직 (F6.1~F6.3)
# 파일 위치: src/services/stats_service.py

from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.stats import (
    AttemptRecord,
    accuracy_by_wordbook,
    accuracy_percent,
    count_study_days,
)
from src.models.entities import StudyRecord, Wordbook, Word


def load_attempt_records(session: Session) -> List[AttemptRecord]:
    """학습 기록 전체를 값 객체 목록으로 읽는다."""
    statement = (
        select(Word.wordbook_id, StudyRecord.is_correct, StudyRecord.studied_on)
        .join(Word, Word.id == StudyRecord.word_id)
    )
    return [
        AttemptRecord(wordbook_id=row[0], is_correct=row[1], attempted_on=row[2])
        for row in session.execute(statement).all()
    ]


def get_overall_stats(session: Session) -> Tuple[Optional[float], int]:
    """전체 정답률(없으면 None)과 학습 일수를 돌려준다. (REQ-022, REQ-023)"""
    records = load_attempt_records(session)
    return accuracy_percent(records), count_study_days(records)


def get_wordbook_accuracies(session: Session) -> List[Tuple[str, Optional[float]]]:
    """단어장 이름과 정답률 목록을 돌려준다. 학습 기록이 없는 단어장은 None. (REQ-024)"""
    rates = accuracy_by_wordbook(load_attempt_records(session))
    wordbooks = session.scalars(select(Wordbook).order_by(Wordbook.id)).all()
    return [(wordbook.name, rates.get(wordbook.id)) for wordbook in wordbooks]

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - DB 학습 기록을 통계 순수 함수에 넘기는 통계 업무 로직 (F6.1~F6.3)
# 파일 위치: src/services/stats_service.py

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.core.stats import (
    AttemptRecord,
    accuracy_by_wordbook,
    accuracy_percent,
    count_study_days,
)
from src.models.entities import StudyRecord, QuizAnswer, Wordbook, Word


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


def get_top_missed_words(session: Session, limit: int = 5) -> List[Tuple[str, int]]:
    """자주 틀린 단어 상위 N개: (단어, 틀린 횟수). 틀린 횟수가 0인 단어는 빼고 큰 순서로 정렬한다. (VOCA-FR-033)"""
    missed: Dict[int, int] = defaultdict(int)
    for word_id, count in session.execute(
        select(StudyRecord.word_id, func.count()).where(StudyRecord.is_correct.is_(False)).group_by(StudyRecord.word_id)
    ).all():
        missed[word_id] += count
    for word_id, count in session.execute(
        select(QuizAnswer.word_id, func.count()).where(QuizAnswer.is_correct.is_(False)).group_by(QuizAnswer.word_id)
    ).all():
        missed[word_id] += count

    ranked = sorted(((count, word_id) for word_id, count in missed.items() if count > 0), reverse=True)[:limit]
    result = []
    for count, word_id in ranked:
        word = session.get(Word, word_id)
        if word is not None:
            result.append((word.word, count))
    return result

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - 오늘의 복습 대상 조회와 단어장별 그룹화 (F5.1, F5.2)
# 파일 위치: src/services/review_service.py

from __future__ import annotations

from datetime import date
from typing import Dict, List, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.entities import Wordbook, Word


def list_due_words(session: Session, today: date) -> List[Word]:
    """다음 복습일이 오늘 이전이거나 오늘인 단어를 돌려준다. (REQ-019)"""
    statement = (
        select(Word)
        .where(Word.next_review_date <= today)
        .order_by(Word.wordbook_id, Word.id)
    )
    return list(session.scalars(statement).all())


def list_due_word_ids(session: Session, today: date) -> List[int]:
    """복습 세션의 대상 id 목록. (REQ-020)"""
    return [word.id for word in list_due_words(session, today)]


def group_due_words_by_wordbook(
    session: Session, today: date
) -> List[Tuple[Wordbook, List[Word]]]:
    """복습 대상을 단어장별로 묶는다. 단어장 순서는 id 순이다. (REQ-019)"""
    groups: Dict[int, Tuple[Wordbook, List[Word]]] = {}
    for word in list_due_words(session, today):
        if word.wordbook_id not in groups:
            groups[word.wordbook_id] = (word.wordbook, [])
        groups[word.wordbook_id][1].append(word)
    return list(groups.values())

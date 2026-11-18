#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - 정답률·학습 일수 계산 순수 함수 (F6.1~F6.3)
# 파일 위치: src/core/stats.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, List, Optional


@dataclass(frozen=True)
class AttemptRecord:
    """학습 이력 한 건. DB 모델과 분리된 값 객체다. (REQ-015)"""

    wordbook_id: int
    is_correct: bool
    attempted_on: date


def accuracy_percent(records: Iterable[AttemptRecord]) -> Optional[float]:
    """정답 수 / 시도 수를 백분율(소수 첫째 자리)로 돌려준다. 기록이 없으면 None. (REQ-022)"""
    items: List[AttemptRecord] = list(records)
    if not items:
        return None
    correct_count = sum(1 for item in items if item.is_correct)
    return round(correct_count * 100 / len(items), 1)


def count_study_days(records: Iterable[AttemptRecord]) -> int:
    """학습 이력이 있는 서로 다른 날짜 수를 센다. (REQ-023)"""
    return len({item.attempted_on for item in records})


def accuracy_by_wordbook(records: Iterable[AttemptRecord]) -> Dict[int, Optional[float]]:
    """단어장 id별 정답률 사전을 만든다. (REQ-024)"""
    grouped: Dict[int, List[AttemptRecord]] = {}
    for item in records:
        grouped.setdefault(item.wordbook_id, []).append(item)
    return {wordbook_id: accuracy_percent(items) for wordbook_id, items in grouped.items()}

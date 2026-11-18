#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - 복습 스케줄 계산 (F4.1, F4.3), 고정 간격 구현체 포함
# 파일 위치: src/core/scheduler.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol, Sequence

from src.core import config


@dataclass(frozen=True)
class ReviewState:
    """단어 한 개의 복습 상태. stage는 간격 목록의 위치(0부터)다. (REQ-016)"""

    stage: int
    next_review_date: date


class ReviewScheduler(Protocol):
    """복습 계산기 인터페이스. 알고리즘을 바꿀 때 이 인터페이스만 맞추면 된다. (REQ-018, F4.3)"""

    def calculate(self, state: ReviewState, is_correct: bool, today: date) -> ReviewState:
        ...


class FixedIntervalScheduler:
    """고정 간격 규칙 구현체. 정답이면 다음 간격으로, 오답이면 짧은 간격으로 되돌린다.

    예: 간격 (1, 3, 7, 14, 30)이면 정답이 이어질 때 1→3→7→14→30일 뒤로 밀리고,
    마지막 간격 이후에는 30일을 유지한다. (REQ-016, REQ-017)
    """

    def __init__(self, interval_days: Sequence[int], wrong_interval_days: int):
        if not interval_days:
            raise ValueError("복습 간격 목록은 비어 있을 수 없습니다.")
        self._interval_days = tuple(interval_days)
        self._wrong_interval_days = wrong_interval_days

    def calculate(self, state: ReviewState, is_correct: bool, today: date) -> ReviewState:
        last_index = len(self._interval_days) - 1
        if not is_correct:
            # 오답이면 처음 단계로 되돌리고 짧은 간격 뒤에 다시 본다.
            return ReviewState(
                stage=0,
                next_review_date=today + timedelta(days=self._wrong_interval_days),
            )
        gap_days = self._interval_days[min(state.stage, last_index)]
        next_stage = min(state.stage + 1, last_index)
        return ReviewState(
            stage=next_stage,
            next_review_date=today + timedelta(days=gap_days),
        )


def create_initial_state(today: date) -> ReviewState:
    """새로 추가된 단어의 초기 상태. 추가한 날 바로 복습 대상이 된다 (가정, 요구사항 확인 필요)."""
    return ReviewState(stage=0, next_review_date=today)


def create_default_scheduler() -> FixedIntervalScheduler:
    """config의 제안 간격으로 기본 계산기를 만든다."""
    return FixedIntervalScheduler(
        interval_days=config.REVIEW_INTERVAL_DAYS,
        wrong_interval_days=config.WRONG_ANSWER_INTERVAL_DAYS,
    )

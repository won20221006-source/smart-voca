#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - 복습 스케줄 계산 단위 테스트 (REQ-016~018)
# 파일 위치: tests/test_scheduler.py
# 실행: python -m unittest discover -s tests -v  (프로젝트 루트에서)

from __future__ import annotations

import unittest
from datetime import date

from src.core.scheduler import (
    FixedIntervalScheduler,
    ReviewState,
    create_default_scheduler,
    create_initial_state,
)

TODAY = date(2026, 11, 18)
INTERVALS = (1, 3, 7, 14, 30)


class FixedIntervalSchedulerTest(unittest.TestCase):
    def setUp(self):
        self.scheduler = FixedIntervalScheduler(INTERVALS, wrong_interval_days=1)

    def test_정답이_이어지면_간격이_1_3_7_14_30일로_늘어난다(self):
        # REQ-016, REQ-017
        state = create_initial_state(TODAY)
        gaps = []
        for _ in range(5):
            state = self.scheduler.calculate(state, is_correct=True, today=TODAY)
            gaps.append((state.next_review_date - TODAY).days)
        self.assertEqual(gaps, [1, 3, 7, 14, 30])

    def test_마지막_간격_이후에는_30일을_유지한다(self):
        # REQ-017
        state = ReviewState(stage=4, next_review_date=TODAY)
        state = self.scheduler.calculate(state, is_correct=True, today=TODAY)
        self.assertEqual(state.stage, 4)
        self.assertEqual((state.next_review_date - TODAY).days, 30)

    def test_오답이면_1일_뒤로_되돌아가고_단계가_0이_된다(self):
        # REQ-016
        state = ReviewState(stage=3, next_review_date=TODAY)
        state = self.scheduler.calculate(state, is_correct=False, today=TODAY)
        self.assertEqual(state.stage, 0)
        self.assertEqual(state.next_review_date, date(2026, 11, 19))

    def test_새_단어는_추가한_날_복습_대상이다(self):
        # 가정: 요구사항 확인 필요 (F5.1 기준 다음 복습일 <= 오늘)
        state = create_initial_state(TODAY)
        self.assertEqual(state.stage, 0)
        self.assertEqual(state.next_review_date, TODAY)

    def test_간격_목록이_비어있으면_오류를_낸다(self):
        # REQ-018
        with self.assertRaises(ValueError):
            FixedIntervalScheduler((), wrong_interval_days=1)


class DefaultSchedulerTest(unittest.TestCase):
    def test_config_상수로_기본_계산기를_만든다(self):
        # REQ-017: 간격 숫자를 코드에 직접 쓰지 않고 config에서 읽는다
        scheduler = create_default_scheduler()
        state = scheduler.calculate(create_initial_state(TODAY), is_correct=True, today=TODAY)
        self.assertEqual((state.next_review_date - TODAY).days, 1)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - 학습 통계 계산 단위 테스트 (REQ-022~024)
# 파일 위치: tests/test_stats.py
# 실행: python -m unittest discover -s tests -v  (프로젝트 루트에서)

from __future__ import annotations

import unittest
from datetime import date

from src.core.stats import (
    AttemptRecord,
    accuracy_by_wordbook,
    accuracy_percent,
    count_study_days,
)

DAY_1 = date(2026, 11, 17)
DAY_2 = date(2026, 11, 18)


class AccuracyPercentTest(unittest.TestCase):
    def test_기록이_없으면_None을_돌려준다(self):
        # REQ-022
        self.assertIsNone(accuracy_percent([]))

    def test_정답률을_소수_첫째_자리로_계산한다(self):
        # REQ-022: 2/3 = 66.7%
        records = [
            AttemptRecord(1, True, DAY_1),
            AttemptRecord(1, True, DAY_1),
            AttemptRecord(1, False, DAY_2),
        ]
        self.assertEqual(accuracy_percent(records), 66.7)


class CountStudyDaysTest(unittest.TestCase):
    def test_서로_다른_날짜만_센다(self):
        # REQ-023
        records = [
            AttemptRecord(1, True, DAY_1),
            AttemptRecord(2, False, DAY_1),
            AttemptRecord(1, True, DAY_2),
        ]
        self.assertEqual(count_study_days(records), 2)


class AccuracyByWordbookTest(unittest.TestCase):
    def test_단어장별로_정답률을_나눈다(self):
        # REQ-024
        records = [
            AttemptRecord(1, True, DAY_1),
            AttemptRecord(1, False, DAY_1),
            AttemptRecord(2, True, DAY_2),
        ]
        self.assertEqual(accuracy_by_wordbook(records), {1: 50.0, 2: 100.0})


if __name__ == "__main__":
    unittest.main()

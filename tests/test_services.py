#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - 서비스 계층 통합 테스트: 메모리 SQLite로 업무 규칙 검증 (REQ-001~024, NFR-009)
# 파일 위치: tests/test_services.py
# 실행: python -m unittest discover -s tests -v  (프로젝트 루트에서)

from __future__ import annotations

import unittest
from datetime import date, datetime

from sqlalchemy import func, select

from src.core.errors import DuplicateWordError, ValidationError
from src.models.database import create_app_engine, create_session_factory, init_db
from src.models.entities import StudyRecord, Word
from src.services.review_service import group_due_words_by_wordbook, list_due_word_ids
from src.services.stats_service import get_overall_stats, get_wordbook_accuracies
from src.services.study_service import record_answer
from src.services.word_service import add_word, delete_word, update_word
from src.services.wordbook_service import (
    create_wordbook,
    delete_wordbook,
    list_wordbooks_with_counts,
    rename_wordbook,
)

TODAY = date(2026, 11, 18)
NOON = datetime(2026, 11, 18, 12, 0)


class ServiceTestCase(unittest.TestCase):
    def setUp(self):
        engine = create_app_engine("sqlite://")
        init_db(engine)
        self.session = create_session_factory(engine)()

    def tearDown(self):
        self.session.close()


class WordbookServiceTest(ServiceTestCase):
    def test_단어장을_만들고_단어_수와_함께_조회한다(self):
        # REQ-001, REQ-002
        wordbook = create_wordbook(self.session, "  수능 단어  ")
        add_word(self.session, wordbook.id, "apple", "사과", None, TODAY)

        rows = list_wordbooks_with_counts(self.session)
        self.assertEqual([(row[0].name, row[1]) for row in rows], [("수능 단어", 1)])

    def test_이름이_공백이면_저장하지_않는다(self):
        # REQ-001
        with self.assertRaises(ValidationError):
            create_wordbook(self.session, "   ")

    def test_이름을_수정한다(self):
        # REQ-003
        wordbook = create_wordbook(self.session, "old")
        rename_wordbook(self.session, wordbook.id, "new")
        self.assertEqual(self.session.get(type(wordbook), wordbook.id).name, "new")

    def test_단어장을_삭제하면_단어와_학습기록도_함께_사라진다(self):
        # REQ-004, NFR-009
        wordbook = create_wordbook(self.session, "삭제 대상")
        word = add_word(self.session, wordbook.id, "apple", "사과", None, TODAY)
        record_answer(self.session, word.id, True, NOON)

        delete_wordbook(self.session, wordbook.id)

        self.assertEqual(self.session.scalar(select(func.count(Word.id))), 0)
        self.assertEqual(self.session.scalar(select(func.count(StudyRecord.id))), 0)


class WordServiceTest(ServiceTestCase):
    def setUp(self):
        super().setUp()
        self.wordbook = create_wordbook(self.session, "단어장")

    def test_단어와_뜻을_추가하고_예문은_선택이다(self):
        # REQ-005, REQ-006
        word = add_word(self.session, self.wordbook.id, " apple ", " 사과 ", "  ", TODAY)
        self.assertEqual((word.word, word.meaning, word.example), ("apple", "사과", None))

    def test_뜻이_비어있으면_추가하지_않는다(self):
        # REQ-005
        with self.assertRaises(ValidationError):
            add_word(self.session, self.wordbook.id, "apple", "", None, TODAY)

    def test_같은_단어장에서_대소문자만_다른_중복은_거부한다(self):
        # REQ-010
        add_word(self.session, self.wordbook.id, "Apple", "사과", None, TODAY)
        with self.assertRaises(DuplicateWordError):
            add_word(self.session, self.wordbook.id, "  apple ", "사과2", None, TODAY)

    def test_다른_단어장에는_같은_단어를_넣을_수_있다(self):
        # REQ-010: 중복 검사 범위는 단어장 안으로 한정
        other = create_wordbook(self.session, "다른 단어장")
        add_word(self.session, self.wordbook.id, "apple", "사과", None, TODAY)
        add_word(self.session, other.id, "apple", "사과", None, TODAY)

    def test_수정할_때_자기_자신은_중복으로_보지_않는다(self):
        # REQ-008, REQ-010
        word = add_word(self.session, self.wordbook.id, "apple", "사과", None, TODAY)
        updated = update_word(self.session, word.id, "APPLE", "사과 (수정)", "An apple.")
        self.assertEqual((updated.word, updated.example), ("APPLE", "An apple."))

    def test_단어를_삭제한다(self):
        # REQ-009
        word = add_word(self.session, self.wordbook.id, "apple", "사과", None, TODAY)
        self.assertEqual(delete_word(self.session, word.id), self.wordbook.id)
        self.assertEqual(self.session.scalar(select(func.count(Word.id))), 0)


class StudyAndReviewTest(ServiceTestCase):
    def setUp(self):
        super().setUp()
        self.wordbook = create_wordbook(self.session, "복습")
        self.apple = add_word(self.session, self.wordbook.id, "apple", "사과", None, TODAY)
        self.pear = add_word(self.session, self.wordbook.id, "pear", "배", None, TODAY)

    def test_정답이면_다음_복습일이_1일_뒤로_잡힌다(self):
        # REQ-013, REQ-016, REQ-017
        record_answer(self.session, self.apple.id, True, NOON)
        self.assertEqual(self.apple.review_stage, 1)
        self.assertEqual(self.apple.next_review_date, date(2026, 11, 19))

    def test_오답이면_1일_뒤로_되돌아간다(self):
        # REQ-016
        record_answer(self.session, self.apple.id, True, NOON)
        record_answer(self.session, self.apple.id, True, NOON)
        record_answer(self.session, self.apple.id, False, NOON)
        self.assertEqual(self.apple.review_stage, 0)
        self.assertEqual(self.apple.next_review_date, date(2026, 11, 19))

    def test_학습_기록은_정답_여부와_날짜를_남긴다(self):
        # REQ-015
        record_answer(self.session, self.apple.id, False, NOON)
        record = self.session.scalars(select(StudyRecord)).one()
        self.assertFalse(record.is_correct)
        self.assertEqual(record.studied_on, TODAY)

    def test_오늘_복습_대상은_다음_복습일이_오늘_이전이거나_오늘인_단어다(self):
        # REQ-019
        record_answer(self.session, self.apple.id, True, NOON)  # 다음 복습일 11-19
        self.assertEqual(list_due_word_ids(self.session, TODAY), [self.pear.id])

    def test_복습_대상은_단어장별로_묶인다(self):
        # REQ-019
        groups = group_due_words_by_wordbook(self.session, TODAY)
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0][0].name, "복습")
        self.assertEqual([word.word for word in groups[0][1]], ["apple", "pear"])


class StatsServiceTest(ServiceTestCase):
    def test_전체_정답률과_학습_일수와_단어장별_정답률을_계산한다(self):
        # REQ-022, REQ-023, REQ-024
        wordbook = create_wordbook(self.session, "통계")
        word = add_word(self.session, wordbook.id, "apple", "사과", None, TODAY)
        record_answer(self.session, word.id, True, NOON)
        record_answer(self.session, word.id, False, NOON)

        accuracy, study_days = get_overall_stats(self.session)
        self.assertEqual((accuracy, study_days), (50.0, 1))
        self.assertEqual(get_wordbook_accuracies(self.session), [("통계", 50.0)])

    def test_기록이_없으면_정답률은_None이다(self):
        # REQ-022
        accuracy, study_days = get_overall_stats(self.session)
        self.assertEqual((accuracy, study_days), (None, 0))


if __name__ == "__main__":
    unittest.main()

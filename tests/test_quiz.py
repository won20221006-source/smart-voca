#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-25 - smart-voca - 시험 기능 테스트: 출제 규칙, 채점, 화면 흐름, 검색·자주 틀린 단어 (VOCA-FR-004, 021~026, 033)
# 파일 위치: tests/test_quiz.py
# 실행: python -m unittest discover -s tests -v  (프로젝트 루트에서)

from __future__ import annotations

import random
import re
import unittest
from datetime import date, datetime

from fastapi.testclient import TestClient
from sqlalchemy import select

from src.app import create_app
from src.core import quiz
from src.core.errors import ValidationError
from src.models.entities import QuizAnswer, StudyRecord, Word
from src.services.stats_service import get_top_missed_words
from src.services.test_service import build_test_questions, grade_test_answers


class QuizRulesTest(unittest.TestCase):
    def test_처음_보는_단어는_가중치가_더_크다(self):
        # VOCA-FR-022
        fresh = quiz.question_weight(tested_before=False, wrong_count=0, days_since_last_test=0)
        seen = quiz.question_weight(tested_before=True, wrong_count=0, days_since_last_test=0)
        self.assertGreater(fresh, seen)

    def test_자주_틀린_단어는_가중치가_더_크다(self):
        # VOCA-FR-022
        missed = quiz.question_weight(True, wrong_count=4, days_since_last_test=0)
        clean = quiz.question_weight(True, wrong_count=0, days_since_last_test=0)
        self.assertGreater(missed, clean)

    def test_가중치_표집은_요청한_개수만큼_서로_다른_인덱스를_낸다(self):
        picked = quiz.pick_weighted_indexes([1.0, 5.0, 1.0, 1.0], 3, random.Random(1))
        self.assertEqual(len(picked), 3)
        self.assertEqual(len(set(picked)), 3)

    def test_섞기_방향은_영한_또는_한영_중_하나다(self):
        rng = random.Random(3)
        directions = {quiz.resolve_direction(quiz.DIRECTION_MIXED, rng) for _ in range(30)}
        self.assertEqual(directions, {quiz.DIRECTION_EN_KO, quiz.DIRECTION_KO_EN})

    def test_한영_방향이면_뜻이_문제가_된다(self):
        prompt, answer = quiz.prompt_and_answer("apple", "사과", quiz.DIRECTION_KO_EN)
        self.assertEqual((prompt, answer), ("사과", "apple"))

    def test_보기는_정답을_포함한_4개다(self):
        options = quiz.build_choice_options("사과", ["배", "포도", "귤", "수박", "사과"], random.Random(0))
        self.assertEqual(len(options), quiz.CHOICE_OPTION_COUNT)
        self.assertIn("사과", options)
        self.assertEqual(len(set(options)), len(options))

    def test_단답은_대소문자와_공백을_무시한다(self):
        self.assertTrue(quiz.grade_short_answer("  Apple ", "apple"))
        self.assertFalse(quiz.grade_short_answer("pear", "apple"))

    def test_OX는_참거짓과_표시가_맞아야_정답이다(self):
        self.assertTrue(quiz.grade_ox_answer("O", statement_is_true=True))
        self.assertTrue(quiz.grade_ox_answer("X", statement_is_true=False))
        self.assertFalse(quiz.grade_ox_answer("O", statement_is_true=False))
        self.assertFalse(quiz.grade_ox_answer("", statement_is_true=True))


class QuizServiceTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(create_app("sqlite://"))
        self.client.post("/wordbooks", data={"name": "수능"})
        for word, meaning in [("apple", "사과"), ("pear", "배"), ("grape", "포도")]:
            self.client.post("/wordbooks/1/words", data={"word": word, "meaning": meaning, "example": ""})
        self.session_factory = self.client.app.state.session_factory

    def test_시험_옵션이_잘못되면_거절한다(self):
        session = self.session_factory()
        try:
            with self.assertRaises(ValidationError):
                build_test_questions(session, 1, 0, quiz.DIRECTION_MIXED, quiz.FORMAT_SHORT, date(2026, 11, 25))
            with self.assertRaises(ValidationError):
                build_test_questions(session, 1, 3, "중국어", quiz.FORMAT_SHORT, date(2026, 11, 25))
        finally:
            session.close()

    def test_문제_수가_단어_수보다_많으면_단어_수만큼만_낸다(self):
        session = self.session_factory()
        try:
            questions = build_test_questions(
                session, 1, 10, quiz.DIRECTION_EN_KO, quiz.FORMAT_SHORT, date(2026, 11, 25), random.Random(0)
            )
            self.assertEqual(len(questions), 3)
            self.assertTrue(all("answer" not in question for question in questions))
        finally:
            session.close()

    def test_채점하면_문항별_기록이_남는다(self):
        # VOCA-FR-026
        session = self.session_factory()
        try:
            submissions = [
                {"word_id": "1", "format": quiz.FORMAT_SHORT, "direction": quiz.DIRECTION_EN_KO, "answer": "사과"},
                {"word_id": "2", "format": quiz.FORMAT_SHORT, "direction": quiz.DIRECTION_EN_KO, "answer": "모름"},
            ]
            results = grade_test_answers(session, submissions, now=datetime(2026, 11, 25, 10, 0))
            self.assertEqual([item["is_correct"] for item in results], [True, False])
            records = session.scalars(select(QuizAnswer).order_by(QuizAnswer.id)).all()
            self.assertEqual([record.is_correct for record in records], [True, False])
            self.assertEqual(records[0].question_format, quiz.FORMAT_SHORT)
            self.assertEqual(records[0].direction, quiz.DIRECTION_EN_KO)
        finally:
            session.close()

    def test_자주_틀린_단어_상위_목록은_틀린_횟수순이다(self):
        # VOCA-FR-033
        session = self.session_factory()
        try:
            session.add_all(
                [
                    StudyRecord(word_id=2, is_correct=False, studied_at=datetime(2026, 11, 25, 9), studied_on=date(2026, 11, 25)),
                    StudyRecord(word_id=2, is_correct=False, studied_at=datetime(2026, 11, 25, 9), studied_on=date(2026, 11, 25)),
                    StudyRecord(word_id=3, is_correct=False, studied_at=datetime(2026, 11, 25, 9), studied_on=date(2026, 11, 25)),
                    StudyRecord(word_id=1, is_correct=True, studied_at=datetime(2026, 11, 25, 9), studied_on=date(2026, 11, 25)),
                ]
            )
            session.commit()
            self.assertEqual(get_top_missed_words(session, limit=2), [("pear", 2), ("grape", 1)])
        finally:
            session.close()


class QuizRouteTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(create_app("sqlite://"))
        self.client.post("/wordbooks", data={"name": "수능"})
        for word, meaning in [("apple", "사과"), ("pear", "배"), ("grape", "포도")]:
            self.client.post("/wordbooks/1/words", data={"word": word, "meaning": meaning, "example": ""})

    def start(self, question_format: str, direction: str = quiz.DIRECTION_EN_KO, count: str = "3"):
        return self.client.post(
            "/wordbooks/1/test",
            data={"count": count, "direction": direction, "format": question_format},
        )

    def parse_questions(self, html: str) -> list:
        word_ids = re.findall(r'name="word_id_(\d+)" value="(\d+)"', html)
        formats = dict(re.findall(r'name="format_(\d+)" value="(\w+)"', html))
        directions = dict(re.findall(r'name="direction_(\d+)" value="(\w+)"', html))
        candidates = dict(re.findall(r'name="candidate_(\d+)" value="([^"]*)"', html))
        return [
            {
                "index": index,
                "word_id": word_id,
                "format": formats[index],
                "direction": directions[index],
                "candidate": candidates.get(index, ""),
            }
            for index, word_id in word_ids
        ]

    def meaning_of(self, word_id: str) -> str:
        return {"1": "사과", "2": "배", "3": "포도"}[word_id]

    def test_시험_옵션_화면이_열린다(self):
        response = self.client.get("/wordbooks/1/test")
        self.assertEqual(response.status_code, 200)
        self.assertIn("시험 시작", response.text)

    def test_단답형_시험을_모두_맞히면_만점이다(self):
        html = self.start(quiz.FORMAT_SHORT).text
        questions = self.parse_questions(html)
        self.assertEqual(len(questions), 3)
        self.assertNotIn("사과", html.split("<form")[0])  # 정답은 시험 화면에 없다
        data = {"total": str(len(questions))}
        for question in questions:
            i = question["index"]
            data[f"word_id_{i}"] = question["word_id"]
            data[f"format_{i}"] = question["format"]
            data[f"direction_{i}"] = question["direction"]
            data[f"candidate_{i}"] = question["candidate"]
            data[f"answer_{i}"] = self.meaning_of(question["word_id"])
        result = self.client.post("/wordbooks/1/test/grade", data=data)
        self.assertIn("점수: 3 / 3", result.text)
        self.assertIn("모두 맞았습니다", result.text)

    def test_틀린_답은_틀린_문항_목록에_나온다(self):
        questions = self.parse_questions(self.start(quiz.FORMAT_SHORT, count="1").text)
        question = questions[0]
        data = {
            "total": "1",
            f"word_id_0": question["word_id"],
            "format_0": question["format"],
            "direction_0": question["direction"],
            "candidate_0": "",
            "answer_0": "틀린답",
        }
        result = self.client.post("/wordbooks/1/test/grade", data=data)
        self.assertIn("점수: 0 / 1", result.text)
        self.assertIn("틀린 문항 (1개)", result.text)
        self.assertIn("틀린답", result.text)

    def test_OX_시험은_제시된_답과_참거짓으로_채점한다(self):
        questions = self.parse_questions(self.start(quiz.FORMAT_OX, direction=quiz.DIRECTION_EN_KO, count="3").text)
        data = {"total": str(len(questions))}
        for question in questions:
            i = question["index"]
            truth = question["candidate"] == self.meaning_of(question["word_id"])
            data[f"word_id_{i}"] = question["word_id"]
            data[f"format_{i}"] = question["format"]
            data[f"direction_{i}"] = question["direction"]
            data[f"candidate_{i}"] = question["candidate"]
            data[f"answer_{i}"] = "O" if truth else "X"
        result = self.client.post("/wordbooks/1/test/grade", data=data)
        self.assertIn("점수: 3 / 3", result.text)

    def test_단어_검색은_영단어와_뜻에서_찾는다(self):
        # VOCA-FR-004
        by_word = self.client.get("/wordbooks/1", params={"q": "PEA"})
        self.assertIn("pear", by_word.text)
        self.assertNotIn("grape", by_word.text)
        by_meaning = self.client.get("/wordbooks/1", params={"q": "포도"})
        self.assertIn("grape", by_meaning.text)
        self.assertNotIn("apple", by_meaning.text)


if __name__ == "__main__":
    unittest.main()

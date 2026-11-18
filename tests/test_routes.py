#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - 웹 화면 흐름 테스트: 단어장 생성→단어 추가→학습→결과 (REQ-001~021)
# 파일 위치: tests/test_routes.py
# 실행: python -m unittest discover -s tests -v  (프로젝트 루트에서)

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from src.app import create_app


class WebFlowTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(create_app("sqlite://"))

    def test_단어장_목록_화면이_열린다(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("아직 단어장이 없습니다", response.text)

    def test_빈_이름으로_단어장을_만들면_오류를_보여준다(self):
        # REQ-001
        response = self.client.post("/wordbooks", data={"name": "  "})
        self.assertEqual(response.status_code, 200)
        self.assertIn("단어장 이름 입력이 필요합니다", response.text)

    def test_단어장_생성부터_학습_결과까지_흐름이_동작한다(self):
        # REQ-001, REQ-005, REQ-011~014
        self.client.post("/wordbooks", data={"name": "수능"})
        self.client.post("/wordbooks/1/words", data={"word": "apple", "meaning": "사과", "example": ""})
        self.client.post("/wordbooks/1/words", data={"word": "pear", "meaning": "배", "example": ""})

        detail = self.client.get("/wordbooks/1")
        self.assertIn("apple", detail.text)
        self.assertIn("pear", detail.text)

        # 학습 시작 → 첫 카드 → 정답, 오답 순서로 답한다.
        card = self.client.get("/wordbooks/1/study")
        self.assertIn("apple", card.text)
        self.client.post(
            "/study/answer",
            data={"word_id": "1", "result": "correct", "ids": "1,2", "correct": "0", "wrong": "0"},
        )
        last_card = self.client.get("/study", params={"ids": "2", "correct": "1", "wrong": "0"})
        self.assertIn("pear", last_card.text)
        self.client.post(
            "/study/answer",
            data={"word_id": "2", "result": "wrong", "ids": "2", "correct": "1", "wrong": "0"},
        )

        result = self.client.get("/study/result", params={"correct": "1", "wrong": "1"})
        self.assertIn("정답률: 50.0%", result.text)

    def test_학습_대상이_없으면_결과_화면으로_간다(self):
        # REQ-014
        # TestClient는 리다이렉트를 따라가므로 최종 화면의 본문을 검사한다.
        response = self.client.get("/study", params={"ids": "", "correct": "0", "wrong": "0"})
        self.assertIn("학습한 단어가 없습니다", response.text)

    def test_오늘_복습할_단어가_없으면_안내한다(self):
        # REQ-021
        response = self.client.get("/review")
        self.assertIn("오늘 복습할 단어가 없습니다", response.text)

    def test_통계_화면이_열리고_기록이_없음을_표시한다(self):
        # REQ-022
        response = self.client.get("/stats")
        self.assertEqual(response.status_code, 200)
        self.assertIn("기록 없음", response.text)


if __name__ == "__main__":
    unittest.main()

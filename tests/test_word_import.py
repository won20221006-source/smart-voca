#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-25 - smart-voca - CSV 일괄 등록 테스트: 머리글·BOM·중복·형식 오류 처리 (VOCA-FR-003)
# 파일 위치: tests/test_word_import.py
# 실행: python -m unittest discover -s tests -v  (프로젝트 루트에서)

from __future__ import annotations

import unittest
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import select

from src.app import create_app
from src.core.errors import ValidationError
from src.models.entities import Word
from src.services.word_import_service import import_words_from_csv


def csv_bytes(text: str, with_bom: bool = True) -> bytes:
    prefix = "﻿" if with_bom else ""
    return (prefix + text).encode("utf-8")


class CsvImportServiceTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(create_app("sqlite://"))
        self.client.post("/wordbooks", data={"name": "수능"})
        self.session_factory = self.client.app.state.session_factory

    def run_import(self, raw_bytes: bytes):
        session = self.session_factory()
        try:
            result = import_words_from_csv(session, 1, raw_bytes, today=date(2026, 11, 25))
            words = [row.word for row in session.scalars(select(Word).order_by(Word.id)).all()]
            return result, words
        finally:
            session.close()

    def test_BOM과_머리글이_있어도_데이터만_등록한다(self):
        # VOCA-FR-003
        result, words = self.run_import(csv_bytes("영단어,뜻\napple,사과\npear,배\n"))
        self.assertEqual(result.added, 2)
        self.assertEqual(words, ["apple", "pear"])

    def test_머리글_없이도_등록한다(self):
        result, words = self.run_import(csv_bytes("apple,사과\n", with_bom=False))
        self.assertEqual(result.added, 1)
        self.assertEqual(words, ["apple"])

    def test_중복은_대소문자와_공백을_무시하고_건너뛴다(self):
        # VOCA-FR-003 중복 정책
        self.run_import(csv_bytes("apple,사과\n"))
        result, words = self.run_import(csv_bytes(" Apple ,사과2\npear,배\npear,배2\n"))
        self.assertEqual(result.added, 1)
        self.assertEqual(result.skipped_duplicate, 2)
        self.assertEqual(words, ["apple", "pear"])

    def test_형식이_잘못된_행은_건너뛰고_센다(self):
        result, words = self.run_import(csv_bytes("apple\n,뜻만\nbanana,바나나\n\n"))
        self.assertEqual(result.added, 1)
        self.assertEqual(result.skipped_invalid, 2)  # 열 부족, 빈 단어
        self.assertEqual(words, ["banana"])

    def test_UTF8이_아니면_거절한다(self):
        with self.assertRaises(ValidationError):
            self.run_import("apple,사과\n".encode("cp949"))

    def test_20MB를_넘으면_거절한다(self):
        with self.assertRaises(ValidationError):
            self.run_import(b"a" * (20 * 1024 * 1024 + 1))


class CsvImportRouteTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(create_app("sqlite://"))
        self.client.post("/wordbooks", data={"name": "수능"})

    def test_업로드하면_결과_안내가_보인다(self):
        response = self.client.post(
            "/wordbooks/1/import",
            files={"file": ("words.csv", csv_bytes("영단어,뜻\napple,사과\n"), "text/csv")},
        )
        self.assertEqual(response.status_code, 200)  # 리다이렉트를 따라간 화면
        self.assertIn("1개 추가", response.text)
        self.assertIn("apple", response.text)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - 입력 검증·중복 키 단위 테스트 (REQ-001, REQ-005, REQ-010)
# 파일 위치: tests/test_validation.py
# 실행: python -m unittest discover -s tests -v  (프로젝트 루트에서)

from __future__ import annotations

import unittest

from src.core.errors import ValidationError
from src.core.validation import (
    WORDBOOK_NAME_MAX_LENGTH,
    clean_optional_text,
    clean_required_text,
    normalize_word_key,
)


class CleanRequiredTextTest(unittest.TestCase):
    def test_앞뒤_공백을_제거한다(self):
        # REQ-001
        self.assertEqual(clean_required_text("  수능 단어  ", "단어장 이름", 50), "수능 단어")

    def test_공백만_입력하면_오류다(self):
        # REQ-001: 필수 항목
        with self.assertRaises(ValidationError):
            clean_required_text("   ", "단어장 이름", WORDBOOK_NAME_MAX_LENGTH)

    def test_None이면_오류다(self):
        with self.assertRaises(ValidationError):
            clean_required_text(None, "뜻", 200)

    def test_최대_길이를_넘으면_오류다(self):
        # REQ-001: 1~50자
        with self.assertRaises(ValidationError):
            clean_required_text("가" * 51, "단어장 이름", WORDBOOK_NAME_MAX_LENGTH)

    def test_최대_길이와_같으면_통과한다(self):
        self.assertEqual(
            clean_required_text("가" * 50, "단어장 이름", WORDBOOK_NAME_MAX_LENGTH),
            "가" * 50,
        )


class CleanOptionalTextTest(unittest.TestCase):
    def test_비어_있으면_None을_돌려준다(self):
        # REQ-006: 예문은 선택 항목
        self.assertIsNone(clean_optional_text("   "))
        self.assertIsNone(clean_optional_text(None))

    def test_값이_있으면_정리해서_돌려준다(self):
        self.assertEqual(clean_optional_text(" I like apples. "), "I like apples.")


class NormalizeWordKeyTest(unittest.TestCase):
    def test_대소문자와_앞뒤_공백을_무시한다(self):
        # REQ-010
        self.assertEqual(normalize_word_key("  Apple "), normalize_word_key("apple"))

    def test_다른_단어는_다른_키를_가진다(self):
        self.assertNotEqual(normalize_word_key("apple"), normalize_word_key("apples"))


if __name__ == "__main__":
    unittest.main()

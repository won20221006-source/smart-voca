#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - 입력값 검증과 중복 비교 키 정규화 (F8.2, F2.6)
# 파일 위치: src/core/validation.py

from __future__ import annotations

from typing import Optional

from src.core.errors import ValidationError

WORDBOOK_NAME_MAX_LENGTH = 50  # REQ-001
WORD_MAX_LENGTH = 100  # REQ-005
MEANING_MAX_LENGTH = 200  # REQ-005


def clean_required_text(value: Optional[str], field_label: str, max_length: int) -> str:
    """앞뒤 공백을 제거한 뒤 필수 입력과 최대 길이를 검사한다.

    공백만 입력된 경우도 빈 값으로 본다. (REQ-001, REQ-005)
    """
    cleaned = (value or "").strip()
    if not cleaned:
        raise ValidationError(f"{field_label} 입력이 필요합니다.")
    if len(cleaned) > max_length:
        raise ValidationError(f"{field_label}: 최대 {max_length}자까지 입력할 수 있습니다.")
    return cleaned


def clean_optional_text(value: Optional[str]) -> Optional[str]:
    """선택 항목(예문 등)을 정리한다. 비어 있으면 None을 돌려준다. (REQ-006)"""
    cleaned = (value or "").strip()
    return cleaned or None


def normalize_word_key(word: str) -> str:
    """같은 단어장 안의 중복 검사에 쓰는 비교 키를 만든다.

    대소문자와 앞뒤 공백을 무시한다. (REQ-010)
    """
    return word.strip().casefold()

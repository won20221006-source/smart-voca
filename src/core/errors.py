#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - 도메인 예외 정의 (F8.5 오류·안내 메시지 처리)
# 파일 위치: src/core/errors.py

from __future__ import annotations


class ValidationError(ValueError):
    """사용자 입력이 규칙(필수 항목, 길이 등)을 어겼을 때 발생한다. (REQ-001, REQ-005)"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class DuplicateWordError(ValueError):
    """같은 단어장에 이미 있는 단어를 추가하려 할 때 발생한다. (REQ-010)"""

    def __init__(self, message: str = "같은 단어장에 이미 있는 단어입니다."):
        super().__init__(message)
        self.message = message

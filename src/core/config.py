#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - 복습 간격 상수와 환경변수 기반 설정 로드 (F4.2, F7.1, F8.3)
# 파일 위치: src/core/config.py

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Tuple

# REQ-017 제안값. 기획서 §9-4(간격 반복 방식) 확정 전까지 임시 사용한다.
# 값을 바꿀 때는 이 상수만 수정하고 코드에 숫자를 직접 쓰지 않는다.
REVIEW_INTERVAL_DAYS: Tuple[int, ...] = (1, 3, 7, 14, 30)
WRONG_ANSWER_INTERVAL_DAYS: int = 1

DEFAULT_DB_PATH = os.path.join("data", "smart_voca.db")
DB_PATH_ENV_NAME = "SMART_VOCA_DB_PATH"


@dataclass(frozen=True)
class AppSettings:
    """애플리케이션 실행 설정. 비밀정보는 이 객체에 담지 않는다 (NFR-004)."""

    db_path: str


def load_settings() -> AppSettings:
    """환경변수에서 설정을 읽는다. 값이 없으면 기본 DB 경로를 쓴다.

    .env 파일 로드는 아직 구현하지 않았다. python-dotenv 도입 승인 후 추가한다.
    """
    return AppSettings(db_path=os.environ.get(DB_PATH_ENV_NAME, DEFAULT_DB_PATH))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - 복습 간격 상수, .env 로드, 환경변수 기반 설정 (F4.2, F7.1, F8.3)
# 파일 위치: src/core/config.py

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

# REQ-017 제안값. 간격 방식은 MVP에서 고정 간격으로 확정 (Decision_Records 참조).
# 값을 바꿀 때는 이 상수만 수정하고 코드에 숫자를 직접 쓰지 않는다.
REVIEW_INTERVAL_DAYS: Tuple[int, ...] = (1, 3, 7, 14, 30)
WRONG_ANSWER_INTERVAL_DAYS: int = 1

DEFAULT_DB_PATH = os.path.join("data", "smart_voca.db")
DB_PATH_ENV_NAME = "DB_PATH"  # 학교 서버 점검 규격(VOCA-SUB-035)에 맞춘 이름
DEFAULT_ENV_FILE = ".env"


@dataclass(frozen=True)
class AppSettings:
    """애플리케이션 실행 설정. 비밀정보는 이 객체에 담지 않는다 (NFR-004)."""

    db_path: str


def parse_env_lines(lines: Iterable[str]) -> Dict[str, str]:
    """KEY=VALUE 형식의 줄을 사전으로 바꾼다. 빈 줄과 # 주석은 무시한다. (F8.3)"""
    values: Dict[str, str] = {}
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def load_env_file(path: str = DEFAULT_ENV_FILE) -> None:
    """.env 파일이 있으면 환경변수로 올린다. 이미 설정된 환경변수는 덮어쓰지 않는다.

    파일이 없으면 아무 일도 하지 않는다. 비밀정보는 이 파일에만 둔다 (NFR-004).
    """
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as env_file:
        for key, value in parse_env_lines(env_file).items():
            os.environ.setdefault(key, value)


def load_settings() -> AppSettings:
    """.env와 환경변수에서 설정을 읽는다. 값이 없으면 기본 DB 경로를 쓴다."""
    load_env_file()
    return AppSettings(db_path=os.environ.get(DB_PATH_ENV_NAME, DEFAULT_DB_PATH))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - 라우트 공통 도구: DB 세션 의존성, 템플릿, 안내 메시지 리다이렉트 (F8.4, F8.5)
# 파일 위치: src/routes/common.py

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterator, List, Optional
from urllib.parse import quote

from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"
TEMPLATES = Jinja2Templates(directory=str(TEMPLATE_DIR))


def get_db_session(request: Request) -> Iterator[Session]:
    """요청마다 DB 세션을 열고 응답 뒤에 닫는다. (F8.1)"""
    session = request.app.state.session_factory()
    try:
        yield session
    finally:
        session.close()


def parse_id_list(raw_value: Optional[str]) -> List[int]:
    """'1,2,3' 형태의 쿼리·폼 값을 정수 목록으로 바꾼다. 숫자가 아닌 토큰은 버린다."""
    if not raw_value:
        return []
    return [int(token) for token in (part.strip() for part in raw_value.split(",")) if token.isdigit()]


def parse_count(raw_value: Optional[str]) -> int:
    """정답·오답 카운터처럼 음수가 아닌 정수를 읽는다. 잘못된 값은 0으로 본다."""
    return int(raw_value) if raw_value and raw_value.isdigit() else 0


def redirect_with_error(url: str, message: str) -> RedirectResponse:
    """오류 메시지를 쿼리 `error`에 담아 같은 서버 경로로 보낸다."""
    separator = "&" if "?" in url else "?"
    return RedirectResponse(f"{url}{separator}error={quote(message)}", status_code=303)


def flash_messages(request: Request) -> Dict[str, Optional[str]]:
    """템플릿에 넘길 안내·오류 메시지 값."""
    return {
        "error": request.query_params.get("error"),
        "notice": request.query_params.get("notice"),
    }

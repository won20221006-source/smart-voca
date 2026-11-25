#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - FastAPI 앱 조립: DB 초기화, 라우터 등록, 입력 오류 처리 (F8.1, F8.3, F8.5)
# 파일 위치: src/app.py

from __future__ import annotations

from typing import Optional
from urllib.parse import urlsplit

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from src.core.config import load_settings
from src.core.errors import DuplicateWordError, NotFoundError, ValidationError
from src.models.database import build_sqlite_url, create_app_engine, create_session_factory, init_db
from src.routes import quiz, review, stats, study, word, wordbook
from src.routes.common import redirect_with_error


def _back_with_error(request: Request, message: str) -> RedirectResponse:
    """오류가 난 화면으로 되돌리며 메시지를 보여준다. 이전 화면을 알 수 없으면 목록으로 간다."""
    referer = request.headers.get("referer")
    path: Optional[str] = urlsplit(referer).path if referer else None
    return redirect_with_error(path or "/", message)


def create_app(database_url: Optional[str] = None) -> FastAPI:
    """앱을 만든다. 테스트에서는 database_url에 메모리 DB를 넘긴다.

    실행: uvicorn src.app:create_app --factory
    """
    url = database_url or build_sqlite_url(load_settings().db_path)
    engine = create_app_engine(url)
    init_db(engine)

    app = FastAPI(title="스마트보카")
    app.state.engine = engine
    app.state.session_factory = create_session_factory(engine)

    @app.exception_handler(ValidationError)
    @app.exception_handler(DuplicateWordError)
    async def handle_input_error(request: Request, exc: ValueError):
        return _back_with_error(request, exc.message)  # type: ignore[attr-defined]

    @app.exception_handler(NotFoundError)
    async def handle_not_found(request: Request, exc: NotFoundError):
        return redirect_with_error("/", exc.message)

    app.include_router(wordbook.router)
    app.include_router(word.router)
    app.include_router(study.router)
    app.include_router(review.router)
    app.include_router(stats.router)
    app.include_router(quiz.router)
    return app

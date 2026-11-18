#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - 오늘의 복습 목록과 복습 세션 시작 라우트 (REQ-019~021)
# 파일 위치: src/routes/review.py

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from src.core.clock import today_local
from src.routes.common import TEMPLATES, flash_messages, get_db_session
from src.services.review_service import group_due_words_by_wordbook, list_due_word_ids
from src.routes.study import build_session_url

router = APIRouter()


@router.get("/review")
def review_list(request: Request, session: Session = Depends(get_db_session)):
    """오늘 복습할 단어를 단어장별로 보여준다. 대상이 없으면 안내 문구. (REQ-019, REQ-021)"""
    groups = group_due_words_by_wordbook(session, today_local())
    total_due = sum(len(words) for _, words in groups)
    return TEMPLATES.TemplateResponse(
        request,
        "review.html",
        {"groups": groups, "total_due": total_due, **flash_messages(request)},
    )


@router.get("/review/start")
def review_start(session: Session = Depends(get_db_session)):
    """복습 대상만으로 학습 세션을 시작한다. (REQ-020, F5.3은 F3.1 재사용)"""
    queue = list_due_word_ids(session, today_local())
    if not queue:
        return RedirectResponse("/review", status_code=303)
    return RedirectResponse(build_session_url(queue, 0, 0), status_code=303)

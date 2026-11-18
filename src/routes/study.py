#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - 학습 세션 화면(카드 제시·정답/오답·결과 요약) 라우트 (REQ-011~015)
# 파일 위치: src/routes/study.py

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from src.routes.common import (
    TEMPLATES,
    flash_messages,
    get_db_session,
    parse_count,
    parse_id_list,
    redirect_with_error,
)
from src.services.study_service import build_study_queue, record_answer
from src.services.word_service import get_word
from src.services.wordbook_service import get_wordbook

router = APIRouter()


def build_session_url(queue: list, correct: int, wrong: int) -> str:
    """남은 대상 id와 정답·오답 카운터를 담은 학습 화면 주소를 만든다."""
    ids_text = ",".join(str(word_id) for word_id in queue)
    return f"/study?ids={ids_text}&correct={correct}&wrong={wrong}"


@router.get("/wordbooks/{wordbook_id}/study")
def study_start(wordbook_id: int, session: Session = Depends(get_db_session)):
    """단어장 단위 학습 세션 시작. 단어가 없으면 안내한다. (REQ-011)"""
    get_wordbook(session, wordbook_id)
    queue = build_study_queue(session, wordbook_id)
    if not queue:
        return redirect_with_error(f"/wordbooks/{wordbook_id}", "단어가 없습니다. 단어를 먼저 추가해 주세요.")
    return RedirectResponse(build_session_url(queue, 0, 0), status_code=303)


@router.get("/study")
def study_card(
    request: Request,
    ids: Optional[str] = None,
    correct: Optional[str] = None,
    wrong: Optional[str] = None,
    session: Session = Depends(get_db_session),
):
    """현재 카드 한 장을 보여준다. 대상이 없으면 결과 화면으로 간다."""
    queue = parse_id_list(ids)
    correct_count = parse_count(correct)
    wrong_count = parse_count(wrong)
    if not queue:
        return RedirectResponse(
            f"/study/result?correct={correct_count}&wrong={wrong_count}", status_code=303
        )
    return TEMPLATES.TemplateResponse(
        request,
        "study_card.html",
        {
            "word": get_word(session, queue[0]),
            "queue": queue,
            "remaining": len(queue),
            "correct": correct_count,
            "wrong": wrong_count,
            **flash_messages(request),
        },
    )


@router.post("/study/answer")
def study_answer(
    word_id: int = Form(...),
    result: str = Form(...),
    ids: str = Form(""),
    correct: str = Form("0"),
    wrong: str = Form("0"),
    session: Session = Depends(get_db_session),
):
    """정답/오답을 기록하고 다음 카드로 넘어간다. (REQ-013, REQ-015)"""
    is_correct = result == "correct"
    record_answer(session, word_id, is_correct, now=datetime.now())

    queue = [queued_id for queued_id in parse_id_list(ids) if queued_id != word_id]
    correct_count = parse_count(correct) + (1 if is_correct else 0)
    wrong_count = parse_count(wrong) + (0 if is_correct else 1)
    return RedirectResponse(build_session_url(queue, correct_count, wrong_count), status_code=303)


@router.get("/study/result")
def study_result(
    request: Request,
    correct: Optional[str] = None,
    wrong: Optional[str] = None,
):
    """세션 결과 요약: 학습 단어 수, 정답 수, 정답률. (REQ-014)"""
    correct_count = parse_count(correct)
    wrong_count = parse_count(wrong)
    total = correct_count + wrong_count
    accuracy = round(correct_count * 100 / total, 1) if total else 0.0
    return TEMPLATES.TemplateResponse(
        request,
        "study_result.html",
        {"total": total, "correct": correct_count, "accuracy": accuracy},
    )

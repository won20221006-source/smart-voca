#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-25 - smart-voca - 시험 화면 라우트: 옵션 고르기, 문제 출제, 채점 결과 (VOCA-FR-021~026)
# 파일 위치: src/routes/quiz.py

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm import Session

from src.core import quiz
from src.core.clock import today_local
from src.core.errors import ValidationError
from src.routes.common import TEMPLATES, get_db_session
from src.services.test_service import build_test_questions, grade_test_answers
from src.services.wordbook_service import get_wordbook

router = APIRouter()

FORMAT_LABELS = {quiz.FORMAT_SHORT: "단답형", quiz.FORMAT_CHOICE: "4지선다", quiz.FORMAT_OX: "OX"}
DIRECTION_LABELS = {quiz.DIRECTION_EN_KO: "영 → 한", quiz.DIRECTION_KO_EN: "한 → 영", quiz.DIRECTION_MIXED: "섞기"}


def parse_question_count(raw_value: str) -> int:
    """문제 수 입력을 정수로 바꾼다. 숫자가 아니면 ValidationError."""
    if not raw_value.strip().isdigit():
        raise ValidationError("문제 수는 숫자로 입력하세요.")
    return int(raw_value)


@router.get("/wordbooks/{wordbook_id}/test")
def test_setup(wordbook_id: int, request: Request, session: Session = Depends(get_db_session)):
    """시험 옵션 화면: 문제 수, 출제 방향, 출제 형식을 고른다."""
    wordbook = get_wordbook(session, wordbook_id)
    return TEMPLATES.TemplateResponse(
        request,
        "quiz_setup.html",
        {
            "wordbook": wordbook,
            "formats": FORMAT_LABELS,
            "directions": DIRECTION_LABELS,
        },
    )


@router.post("/wordbooks/{wordbook_id}/test")
def test_start(
    wordbook_id: int,
    request: Request,
    count: str = Form("10"),
    direction: str = Form(quiz.DIRECTION_MIXED),
    question_format: str = Form(quiz.FORMAT_CHOICE, alias="format"),
    session: Session = Depends(get_db_session),
):
    """옵션대로 문제를 뽑아 시험 화면을 보여 준다. 정답은 화면에 싣지 않는다."""
    wordbook = get_wordbook(session, wordbook_id)
    questions = build_test_questions(
        session,
        wordbook_id,
        parse_question_count(count),
        direction,
        question_format,
        today=today_local(),
    )
    return TEMPLATES.TemplateResponse(
        request,
        "quiz_take.html",
        {
            "wordbook": wordbook,
            "questions": questions,
            "format_label": FORMAT_LABELS[question_format],
        },
    )


@router.post("/wordbooks/{wordbook_id}/test/grade")
async def test_grade(wordbook_id: int, request: Request, session: Session = Depends(get_db_session)):
    """제출된 답을 채점하고 점수와 틀린 문항을 보여 준다. (VOCA-FR-025, VOCA-FR-026)"""
    wordbook = get_wordbook(session, wordbook_id)
    form = await request.form()
    total = parse_question_count(str(form.get("total", "0")))

    submissions = []
    for index in range(total):
        submissions.append(
            {
                "word_id": str(form.get(f"word_id_{index}", "")),
                "format": str(form.get(f"format_{index}", "")),
                "direction": str(form.get(f"direction_{index}", "")),
                "candidate": str(form.get(f"candidate_{index}", "")),
                "answer": str(form.get(f"answer_{index}", "")),
            }
        )
    for submission in submissions:
        if submission["format"] not in quiz.QUIZ_FORMATS or submission["direction"] not in (
            quiz.DIRECTION_EN_KO,
            quiz.DIRECTION_KO_EN,
        ):
            raise ValidationError("시험 정보가 올바르지 않습니다. 다시 시작하세요.")

    results = grade_test_answers(session, submissions, now=datetime.now())
    correct_count = sum(1 for result in results if result["is_correct"])
    return TEMPLATES.TemplateResponse(
        request,
        "quiz_result.html",
        {
            "wordbook": wordbook,
            "results": results,
            "total": len(results),
            "correct": correct_count,
            "wrong_results": [result for result in results if not result["is_correct"]],
            "accuracy": round(correct_count * 100 / len(results), 1) if results else 0.0,
        },
    )

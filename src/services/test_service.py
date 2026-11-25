#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-25 - smart-voca - 시험 출제·채점과 문항별 기록 저장 업무 로직 (VOCA-FR-021~026)
# 파일 위치: src/services/test_service.py

from __future__ import annotations

import random
from collections import defaultdict
from datetime import date, datetime
from typing import Dict, List, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core import quiz
from src.core.clock import today_local
from src.core.errors import ValidationError
from src.models.entities import StudyRecord, QuizAnswer, Word
from src.services.word_service import get_word
from src.services.wordbook_service import get_wordbook


def validate_test_options(count: int, direction: str, question_format: str) -> None:
    """시험 옵션을 검사한다. 잘못된 값이면 ValidationError."""
    if not quiz.QUIZ_MIN_COUNT <= count <= quiz.QUIZ_MAX_COUNT:
        raise ValidationError(f"문제 수는 {quiz.QUIZ_MIN_COUNT}~{quiz.QUIZ_MAX_COUNT}개여야 합니다.")
    if direction not in quiz.QUIZ_DIRECTIONS:
        raise ValidationError("출제 방향을 다시 고르세요.")
    if question_format not in quiz.QUIZ_FORMATS:
        raise ValidationError("출제 형식을 다시 고르세요.")


def load_word_history(session: Session, word_ids: Sequence[int]) -> Dict[int, dict]:
    """단어별 시험 이력: 본 적 있는지, 틀린 횟수, 마지막 학습일.

    틀린 횟수는 암기 기록과 시험 기록을 합쳐 센다.
    """
    history: Dict[int, dict] = defaultdict(lambda: {"tested": False, "wrong": 0, "last_on": None})
    if not word_ids:
        return {}

    for word_id, is_correct, studied_on in session.execute(
        select(StudyRecord.word_id, StudyRecord.is_correct, StudyRecord.studied_on).where(
            StudyRecord.word_id.in_(word_ids)
        )
    ).all():
        _merge_history(history[word_id], is_correct, studied_on)

    for word_id, is_correct, answered_on in session.execute(
        select(QuizAnswer.word_id, QuizAnswer.is_correct, QuizAnswer.answered_on).where(
            QuizAnswer.word_id.in_(word_ids)
        )
    ).all():
        _merge_history(history[word_id], is_correct, answered_on)

    return dict(history)


def _merge_history(entry: dict, is_correct: bool, studied_on: date) -> None:
    entry["tested"] = True
    if not is_correct:
        entry["wrong"] += 1
    if entry["last_on"] is None or studied_on > entry["last_on"]:
        entry["last_on"] = studied_on


def build_test_questions(
    session: Session,
    wordbook_id: int,
    count: int,
    direction: str,
    question_format: str,
    today: date,
    rng: Optional[random.Random] = None,
) -> List[dict]:
    """시험 문항 목록을 만든다. 정답은 화면에 넣지 않는다 (채점은 DB에서 다시 확인한다)."""
    get_wordbook(session, wordbook_id)
    validate_test_options(count, direction, question_format)
    generator = rng or random.Random()

    words = list(session.scalars(select(Word).where(Word.wordbook_id == wordbook_id).order_by(Word.id)).all())
    if not words:
        raise ValidationError("시험을 보려면 단어가 1개 이상 있어야 합니다.")

    history = load_word_history(session, [word.id for word in words])
    weights = []
    for word in words:
        entry = history.get(word.id, {"tested": False, "wrong": 0, "last_on": None})
        days_since = (today - entry["last_on"]).days if entry["last_on"] else 0
        weights.append(quiz.question_weight(entry["tested"], entry["wrong"], days_since))

    picked = quiz.pick_weighted_indexes(weights, min(count, len(words)), generator)
    questions = []
    for index in picked:
        word = words[index]
        item_direction = quiz.resolve_direction(direction, generator)
        prompt, correct_answer = quiz.prompt_and_answer(word.word, word.meaning, item_direction)
        other_answers = [
            quiz.prompt_and_answer(other.word, other.meaning, item_direction)[1]
            for other in words
            if other.id != word.id
        ]
        question = {
            "word_id": word.id,
            "format": question_format,
            "direction": item_direction,
            "prompt": prompt,
            "options": [],
            "candidate": "",
        }
        if question_format == quiz.FORMAT_CHOICE:
            question["options"] = quiz.build_choice_options(correct_answer, other_answers, generator)
        elif question_format == quiz.FORMAT_OX:
            question["candidate"] = quiz.pick_ox_candidate(correct_answer, other_answers, generator)
        questions.append(question)
    return questions


def grade_test_answers(
    session: Session,
    submissions: List[dict],
    now: datetime,
) -> List[dict]:
    """제출된 답을 채점하고 문항별 기록을 남긴다.

    submissions 항목: word_id, format, direction, answer, candidate(OX만).
    정답은 DB의 단어 뜻·단어로 다시 계산한다.
    """
    results = []
    for submission in submissions:
        word = get_word(session, int(submission["word_id"]))
        item_direction = submission["direction"]
        prompt, correct_answer = quiz.prompt_and_answer(word.word, word.meaning, item_direction)
        answer = submission.get("answer", "").strip()
        shown = ""
        display_correct = correct_answer
        display_your = answer

        if submission["format"] == quiz.FORMAT_SHORT:
            is_correct = quiz.grade_short_answer(answer, correct_answer)
        elif submission["format"] == quiz.FORMAT_CHOICE:
            is_correct = quiz.grade_choice_answer(answer, correct_answer)
        else:
            shown = submission.get("candidate", "")
            statement_is_true = quiz.ox_statement_is_true(shown, correct_answer)
            is_correct = quiz.grade_ox_answer(answer, statement_is_true)
            display_correct = "O" if statement_is_true else "X"

        session.add(
            QuizAnswer(
                word_id=word.id,
                question_format=submission["format"],
                direction=item_direction,
                is_correct=is_correct,
                answered_at=now,
                answered_on=today_local(now),
            )
        )
        results.append(
            {
                "prompt": prompt,
                "shown": shown,
                "your_answer": display_your or "(무응답)",
                "correct_answer": display_correct,
                "is_correct": is_correct,
            }
        )
    session.commit()
    return results

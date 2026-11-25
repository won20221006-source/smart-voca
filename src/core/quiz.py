#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-25 - smart-voca - 시험 문제 만들기·채점의 순수 규칙: 출제 가중치, 보기 만들기, 정오 판정 (VOCA-FR-021~025)
# 파일 위치: src/core/quiz.py

from __future__ import annotations

import random
from typing import List, Sequence

FORMAT_SHORT = "short"  # 단답형
FORMAT_CHOICE = "choice"  # 4지선다
FORMAT_OX = "ox"  # 참/거짓
QUIZ_FORMATS = (FORMAT_SHORT, FORMAT_CHOICE, FORMAT_OX)

DIRECTION_EN_KO = "en_ko"  # 영 → 한
DIRECTION_KO_EN = "ko_en"  # 한 → 영
DIRECTION_MIXED = "mixed"  # 섞기 (문제마다 영→한 또는 한→영)
QUIZ_DIRECTIONS = (DIRECTION_EN_KO, DIRECTION_KO_EN, DIRECTION_MIXED)

CHOICE_OPTION_COUNT = 4
QUIZ_MIN_COUNT = 1
QUIZ_MAX_COUNT = 50


def question_weight(tested_before: bool, wrong_count: int, days_since_last_test: int) -> float:
    """출제 가중치. 값이 클수록 뽑힐 확률이 높다 (VOCA-FR-022).

    시험 본 적 없음 +2, 자주 틀린 단어 틀린 횟수당 +1(최대 5회), 오래 안 본 단어 최대 +2(7일마다 +1).
    모든 단어는 최소 1을 가져서 한 번도 뽑히지 않는 단어는 없다.
    """
    weight = 1.0
    if not tested_before:
        weight += 2.0
    weight += min(wrong_count, 5)
    weight += min(days_since_last_test / 7, 2.0)
    return weight


def pick_weighted_indexes(weights: Sequence[float], count: int, rng: random.Random) -> List[int]:
    """가중치에 따라 서로 다른 인덱스를 count개 고른다 (Efraimidis-Spirakis 방식)."""
    keyed = [(rng.random() ** (1.0 / weight), index) for index, weight in enumerate(weights)]
    keyed.sort(reverse=True)
    return [index for _, index in keyed[:count]]


def resolve_direction(direction: str, rng: random.Random) -> str:
    """섞기이면 영→한과 한→영 중 하나를 고른다. 아니면 그대로 쓴다."""
    if direction == DIRECTION_MIXED:
        return rng.choice([DIRECTION_EN_KO, DIRECTION_KO_EN])
    return direction


def prompt_and_answer(word: str, meaning: str, direction: str) -> tuple[str, str]:
    """방향에 따라 문제로 보일 글자와 정답을 돌려준다."""
    if direction == DIRECTION_KO_EN:
        return meaning, word
    return word, meaning


def build_choice_options(
    correct_answer: str,
    other_answers: Sequence[str],
    rng: random.Random,
) -> List[str]:
    """4지선다 보기를 만든다. 정답과 다른 단어의 답에서 오답을 뽑고 섞는다."""
    distractor_pool = sorted({answer for answer in other_answers if answer != correct_answer})
    rng.shuffle(distractor_pool)
    options = [correct_answer] + distractor_pool[: CHOICE_OPTION_COUNT - 1]
    rng.shuffle(options)
    return options


def normalize_answer(text: str) -> str:
    """단답 비교용 정규화: 앞뒤 공백 제거, 연속 공백 한 칸, 대소문자 무시."""
    return " ".join(text.split()).casefold()


def grade_short_answer(user_answer: str, correct_answer: str) -> bool:
    """단답형 정오 판정. 공백과 대소문자 차이는 무시한다."""
    return normalize_answer(user_answer) == normalize_answer(correct_answer)


def grade_choice_answer(user_answer: str, correct_answer: str) -> bool:
    """4지선다 정오 판정. 고른 보기가 정답과 같은지 본다."""
    return user_answer == correct_answer


def ox_statement_is_true(shown_answer: str, correct_answer: str) -> bool:
    """OX 문제에서 제시된 답이 실제 정답과 같은지 (참 문장인지)."""
    return shown_answer == correct_answer


def grade_ox_answer(user_mark: str, statement_is_true: bool) -> bool:
    """O(참)·X(거짓) 표시와 실제 참·거짓이 맞는지 본다."""
    if user_mark not in ("O", "X"):
        return False
    return (user_mark == "O") == statement_is_true


def pick_ox_candidate(correct_answer: str, other_answers: Sequence[str], rng: random.Random) -> str:
    """OX 문제에 보일 답을 고른다. 정답(참)이거나 다른 단어의 답(거짓)이다. 참·거짓은 반반에 가깝게 뽑는다."""
    if rng.random() < 0.5 or not other_answers:
        return correct_answer
    wrong_pool = sorted({answer for answer in other_answers if answer != correct_answer})
    if not wrong_pool:
        return correct_answer
    return rng.choice(wrong_pool)

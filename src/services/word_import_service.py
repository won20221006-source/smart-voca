#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-25 - smart-voca - CSV 파일로 단어 일괄 등록 (VOCA-FR-003). 중복·형식 오류 행은 건너뛴다
# 파일 위치: src/services/word_import_service.py

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import date
from typing import List, Set

from sqlalchemy.orm import Session

from src.core.errors import ValidationError
from src.core.scheduler import create_initial_state
from src.core.validation import (
    MEANING_MAX_LENGTH,
    WORD_MAX_LENGTH,
    clean_required_text,
    normalize_word_key,
)
from src.models.entities import Word
from src.services.word_service import list_words
from src.services.wordbook_service import get_wordbook

CSV_MAX_BYTES = 20 * 1024 * 1024  # 서버 업로드 한도(20MB)와 맞춘다 (Dockerfile 구성 §5)
CSV_HEADER_WORD = "영단어"
CSV_HEADER_MEANING = "뜻"


@dataclass(frozen=True)
class WordImportResult:
    """가져오기 결과. 화면에 몇 개를 넣고 몇 개를 건너뛰었는지 알려 준다."""

    added: int
    skipped_duplicate: int
    skipped_invalid: int


def decode_csv_bytes(raw_bytes: bytes) -> str:
    """UTF-8 (BOM 유무 무관)으로 읽는다. 그 밖의 인코딩은 거절한다.

    제공 CSV는 UTF-8 BOM 파일이므로 utf-8-sig로 읽어 첫 열 이름에 BOM이 붙지 않게 한다.
    """
    if len(raw_bytes) > CSV_MAX_BYTES:
        raise ValidationError("CSV 파일은 20MB까지 가져올 수 있습니다.")
    try:
        return raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValidationError("CSV 파일은 UTF-8 인코딩이어야 합니다.") from error


def is_header_row(row: List[str]) -> bool:
    """첫 행이 `영단어,뜻` 머리글이면 참이다. 머리글은 데이터로 보지 않는다."""
    return len(row) >= 2 and row[0].strip() == CSV_HEADER_WORD and row[1].strip() == CSV_HEADER_MEANING


def import_words_from_csv(
    session: Session,
    wordbook_id: int,
    raw_bytes: bytes,
    today: date,
) -> WordImportResult:
    """CSV(`영단어,뜻`)를 읽어 단어장에 한꺼번에 넣는다.

    중복 정책: 같은 단어장에 이미 있는 단어(대소문자·앞뒤 공백 무시)와
    파일 안에서 먼저 나온 같은 단어는 건너뛴다. 기존 단어는 덮어쓰지 않는다.
    형식이 잘못된 행(열 부족, 빈 값, 길이 초과)도 건너뛰고 개수만 센다.
    """
    get_wordbook(session, wordbook_id)
    text = decode_csv_bytes(raw_bytes)
    rows = list(csv.reader(io.StringIO(text)))
    if rows and is_header_row(rows[0]):
        rows = rows[1:]

    known_keys: Set[str] = {normalize_word_key(existing.word) for existing in list_words(session, wordbook_id)}
    initial_state = create_initial_state(today)
    added = skipped_duplicate = skipped_invalid = 0

    for row in rows:
        if not any(cell.strip() for cell in row):
            continue  # 빈 줄은 세지 않는다
        if len(row) < 2:
            skipped_invalid += 1
            continue
        try:
            cleaned_word = clean_required_text(row[0], "단어", WORD_MAX_LENGTH)
            cleaned_meaning = clean_required_text(row[1], "뜻", MEANING_MAX_LENGTH)
        except ValidationError:
            skipped_invalid += 1
            continue

        key = normalize_word_key(cleaned_word)
        if key in known_keys:
            skipped_duplicate += 1
            continue
        known_keys.add(key)

        session.add(
            Word(
                wordbook_id=wordbook_id,
                word=cleaned_word,
                meaning=cleaned_meaning,
                example=None,
                review_stage=initial_state.stage,
                next_review_date=initial_state.next_review_date,
            )
        )
        added += 1

    session.commit()
    return WordImportResult(added=added, skipped_duplicate=skipped_duplicate, skipped_invalid=skipped_invalid)

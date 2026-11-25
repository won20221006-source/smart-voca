#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - 단어 추가·수정·삭제 요청 처리 라우트 (REQ-005~010, REQ-027)
# 파일 위치: src/routes/word.py

from __future__ import annotations

from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from src.routes.common import get_db_session
from src.services.word_import_service import CSV_MAX_BYTES, import_words_from_csv
from src.services.word_service import add_word, delete_word, update_word
from src.services.wordbook_service import get_wordbook
from src.core.clock import today_local

router = APIRouter()


@router.post("/wordbooks/{wordbook_id}/words")
def word_add(
    wordbook_id: int,
    word: str = Form(""),
    meaning: str = Form(""),
    example: str = Form(""),
    session: Session = Depends(get_db_session),
):
    """단어 추가. 추가한 날이 첫 복습일이다. (REQ-005, REQ-006, REQ-010)"""
    get_wordbook(session, wordbook_id)
    add_word(session, wordbook_id, word, meaning, example, today=today_local())
    return RedirectResponse(f"/wordbooks/{wordbook_id}", status_code=303)


@router.post("/wordbooks/{wordbook_id}/import")
def word_import(
    wordbook_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_db_session),
):
    """CSV(영단어,뜻)로 단어 일괄 등록. 결과 개수를 안내 메시지로 보여 준다. (VOCA-FR-003)"""
    raw_bytes = file.file.read(CSV_MAX_BYTES + 1)  # 한도 확인용으로 한 바이트 더 읽는다
    result = import_words_from_csv(session, wordbook_id, raw_bytes, today=today_local())
    notice = (
        f"{result.added}개 추가 · 중복 {result.skipped_duplicate}개 건너뜀 · "
        f"형식 오류 {result.skipped_invalid}개 건너뜀"
    )
    return RedirectResponse(f"/wordbooks/{wordbook_id}?notice={quote(notice)}", status_code=303)


@router.post("/words/{word_id}/update")
def word_update(
    word_id: int,
    word: str = Form(""),
    meaning: str = Form(""),
    example: str = Form(""),
    session: Session = Depends(get_db_session),
):
    """단어·뜻·예문 수정. (REQ-008)"""
    updated = update_word(session, word_id, word, meaning, example)
    return RedirectResponse(f"/wordbooks/{updated.wordbook_id}", status_code=303)


@router.post("/words/{word_id}/delete")
def word_delete(word_id: int, session: Session = Depends(get_db_session)):
    """단어 삭제. 확인 창은 화면에서 띄운다. (REQ-009)"""
    wordbook_id = delete_word(session, word_id)
    return RedirectResponse(f"/wordbooks/{wordbook_id}", status_code=303)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - 단어장 목록·생성·이름 수정·삭제 화면 라우트 (REQ-001~004)
# 파일 위치: src/routes/wordbook.py

from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from src.routes.common import TEMPLATES, flash_messages, get_db_session
from src.services.wordbook_service import (
    create_wordbook,
    delete_wordbook,
    get_wordbook,
    list_wordbooks_with_counts,
    rename_wordbook,
)
from src.services.word_service import list_words

router = APIRouter()


@router.get("/")
def wordbook_list(request: Request, session: Session = Depends(get_db_session)):
    """단어장 목록 화면. (REQ-002)"""
    return TEMPLATES.TemplateResponse(
        request,
        "wordbooks.html",
        {"rows": list_wordbooks_with_counts(session), **flash_messages(request)},
    )


@router.post("/wordbooks")
def wordbook_create(name: str = Form(""), session: Session = Depends(get_db_session)):
    """단어장 생성. 실패 시 오류는 전역 핸들러가 처리한다. (REQ-001)"""
    create_wordbook(session, name)
    return RedirectResponse("/", status_code=303)


@router.get("/wordbooks/{wordbook_id}")
def wordbook_detail(
    wordbook_id: int,
    request: Request,
    q: str = "",
    session: Session = Depends(get_db_session),
):
    """단어장 상세: 단어 목록과 단어 추가 폼. 검색어가 있으면 영단어·뜻에서 찾는다. (REQ-007, VOCA-FR-004)"""
    wordbook = get_wordbook(session, wordbook_id)
    words = list_words(session, wordbook_id)
    keyword = q.strip().casefold()
    if keyword:
        words = [
            item for item in words
            if keyword in item.word.casefold() or keyword in item.meaning.casefold()
        ]
    return TEMPLATES.TemplateResponse(
        request,
        "wordbook_detail.html",
        {
            "wordbook": wordbook,
            "words": words,
            "query": q.strip(),
            **flash_messages(request),
        },
    )


@router.post("/wordbooks/{wordbook_id}/rename")
def wordbook_rename(
    wordbook_id: int, name: str = Form(""), session: Session = Depends(get_db_session)
):
    """단어장 이름 수정. (REQ-003)"""
    rename_wordbook(session, wordbook_id, name)
    return RedirectResponse(f"/wordbooks/{wordbook_id}", status_code=303)


@router.post("/wordbooks/{wordbook_id}/delete")
def wordbook_delete(wordbook_id: int, session: Session = Depends(get_db_session)):
    """단어장 삭제. 확인 창은 화면에서 띄운다. (REQ-004, NFR-009)"""
    delete_wordbook(session, wordbook_id)
    return RedirectResponse("/", status_code=303)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - 학습 통계 화면 라우트 (REQ-022~024)
# 파일 위치: src/routes/stats.py

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from src.routes.common import TEMPLATES, get_db_session
from src.services.stats_service import get_overall_stats, get_wordbook_accuracies

router = APIRouter()


@router.get("/stats")
def stats_page(request: Request, session: Session = Depends(get_db_session)):
    """전체 정답률, 학습 일수, 단어장별 정답률 화면. (REQ-022~024)"""
    overall_accuracy, study_days = get_overall_stats(session)
    return TEMPLATES.TemplateResponse(
        request,
        "stats.html",
        {
            "overall_accuracy": overall_accuracy,
            "study_days": study_days,
            "by_wordbook": get_wordbook_accuracies(session),
        },
    )

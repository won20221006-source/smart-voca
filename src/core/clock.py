#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - "오늘" 날짜 판단 (F8.6), 테스트에서 시각을 주입할 수 있게 분리
# 파일 위치: src/core/clock.py

from __future__ import annotations

from datetime import date, datetime


def today_local(now: datetime | None = None) -> date:
    """로컬 시간대 기준 오늘 날짜를 돌려준다.

    now를 넘기면 그 시각을 기준으로 삼는다. 테스트에서 "오늘"을 고정하기 위한 장치다.
    (REQ-016, REQ-019, REQ-023)
    """
    current = now if now is not None else datetime.now()
    return current.date()

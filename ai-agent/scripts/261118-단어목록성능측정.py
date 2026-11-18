#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - 단어 1,000개 단어장 상세 화면 렌더링 시간 측정 (NFR-003 근거 자료)
# 파일 위치: ai-agent/scripts/261118-단어목록성능측정.py
# 실행: .venv\Scripts\python.exe ai-agent\scripts\261118-단어목록성능측정.py  (프로젝트 루트에서)

from __future__ import annotations

import sys
import time
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from src.app import create_app  # noqa: E402
from src.services.word_service import add_word  # noqa: E402
from src.services.wordbook_service import create_wordbook  # noqa: E402

WORD_COUNT = 1000
RUNS = 5


def main() -> None:
    app = create_app("sqlite://")
    session = app.state.session_factory()
    wordbook = create_wordbook(session, "성능 측정")
    for index in range(WORD_COUNT):
        add_word(session, wordbook.id, f"word{index:04d}", f"뜻{index}", f"예문 {index}", date(2026, 11, 18))
    session.close()

    client = TestClient(app)
    page = f"/wordbooks/{wordbook.id}"
    client.get(page)  # 첫 요청은 준비 비용이 있어 측정에서 뺀다
    timings = []
    for _ in range(RUNS):
        start = time.perf_counter()
        response = client.get(page)
        timings.append(time.perf_counter() - start)

    assert response.status_code == 200
    assert f"word{WORD_COUNT - 1:04d}" in response.text
    print(f"단어 {WORD_COUNT}개 상세 화면: 중앙값 {sorted(timings)[RUNS // 2] * 1000:.1f} ms, 최대 {max(timings) * 1000:.1f} ms")


if __name__ == "__main__":
    main()

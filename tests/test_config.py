#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - 설정 파일 파싱과 환경변수 우선순위 테스트 (F8.3, NFR-004)
# 파일 위치: tests/test_config.py
# 실행: python -m unittest discover -s tests -v  (프로젝트 루트에서)

from __future__ import annotations

import os
import tempfile
import unittest

from src.core.config import (
    DB_PATH_ENV_NAME,
    DEFAULT_DB_PATH,
    load_env_file,
    parse_env_lines,
)


class ParseEnvLinesTest(unittest.TestCase):
    def test_주석과_빈_줄은_무시하고_따옴표를_벗긴다(self):
        lines = ["# 주석", "", "A=1", 'B="two"', "C='three'", "잘못된줄"]
        self.assertEqual(parse_env_lines(lines), {"A": "1", "B": "two", "C": "three"})


class LoadEnvFileTest(unittest.TestCase):
    def setUp(self):
        self.saved_value = os.environ.pop(DB_PATH_ENV_NAME, None)

    def tearDown(self):
        os.environ.pop(DB_PATH_ENV_NAME, None)
        if self.saved_value is not None:
            os.environ[DB_PATH_ENV_NAME] = self.saved_value

    def test_파일이_없으면_아무것도_하지_않는다(self):
        load_env_file(os.path.join(tempfile.gettempdir(), "no-such-smart-voca.env"))
        self.assertNotIn(DB_PATH_ENV_NAME, os.environ)

    def test_파일의_값을_환경변수로_올리되_기존_값은_유지한다(self):
        with tempfile.NamedTemporaryFile("w", suffix=".env", delete=False, encoding="utf-8") as handle:
            handle.write(f"{DB_PATH_ENV_NAME}=from_file.db\n")
            path = handle.name
        try:
            load_env_file(path)
            self.assertEqual(os.environ[DB_PATH_ENV_NAME], "from_file.db")

            os.environ[DB_PATH_ENV_NAME] = "from_shell.db"
            load_env_file(path)
            self.assertEqual(os.environ[DB_PATH_ENV_NAME], "from_shell.db")
        finally:
            os.remove(path)

    def test_기본_DB_경로는_data_폴더_아래다(self):
        self.assertEqual(os.path.normpath(DEFAULT_DB_PATH), os.path.join("data", "smart_voca.db"))


if __name__ == "__main__":
    unittest.main()

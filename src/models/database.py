#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2026-11-18 - smart-voca - SQLite 엔진·세션 생성과 테이블 초기화 (F8.1, NFR-002, NFR-009)
# 파일 위치: src/models/database.py

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    """모든 ORM 모델의 기반 클래스."""


def build_sqlite_url(db_path: str) -> str:
    """파일 경로를 SQLAlchemy용 SQLite URL로 바꾼다."""
    return f"sqlite:///{Path(db_path).as_posix()}"


def create_app_engine(database_url: str) -> Engine:
    """SQLite 엔진을 만든다. 외래키 CASCADE가 동작하도록 PRAGMA foreign_keys를 켠다. (NFR-009)

    메모리 DB(`sqlite://`)는 테스트용이며, 모든 연결이 같은 DB를 보도록 StaticPool을 쓴다.
    """
    connect_args = {"check_same_thread": False}
    is_memory = database_url in ("sqlite://", "sqlite:///:memory:")
    engine = create_engine(
        database_url,
        connect_args=connect_args,
        poolclass=StaticPool if is_memory else None,
    )

    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """요청마다 새 세션을 만드는 팩토리를 돌려준다."""
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db(engine: Engine) -> None:
    """모델에 정의된 테이블이 없으면 만든다. 모델 모듈을 먼저 import해야 테이블이 등록된다."""
    from src.models import entities  # noqa: F401  (테이블 등록용 import)

    if engine.url.database and engine.url.database != ":memory:":
        Path(engine.url.database).parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(engine)

# 시스템 아키텍처 설계서

**파일 위치**: `ai-agent/claude/261125_기말과제/smart-voca_Architecture_Design_v1.0_261125.md`
**작성일**: 2026-11-25
**버전**: v1.0
**설명**: 계층 구조, 요청 흐름, 배포 구성과 과제 요구사항(VOCA-SUB-014) 대응

---

## 1. 구성 요약

| 항목 | 선택 | 근거 |
|---|---|---|
| 언어·프레임워크 | Python 3.12, FastAPI | CLAUDE.md 스택, 과제 허용 목록 |
| 화면 | Jinja2 서버 렌더링, 최소 JS 없음 | 로그인·세션 없는 1인 앱 |
| DB | SQLite 한 파일 | VOCA-SUB-035 (PostgreSQL 미사용) |
| 실행 | uvicorn, 컨테이너 8080 포트 | VOCA-SUB-032 |
| 배포 | Dockerfile, UID 10001 | VOCA-SUB-031, 034 |

## 2. 계층 구조

```
src/
  app.py          앱 조립 (DB 초기화, 라우터 등록, 입력 오류 처리)
  routes/         HTTP 요청·응답, 템플릿 선택, 폼 값 읽기
  services/       업무 규칙과 DB 조작 (트랜잭션 단위)
  core/           DB와 무관한 순수 규칙 (복습 간격, 출제 가중치, 채점, 통계 계산, 검증)
  models/         SQLAlchemy 모델, 세션 생성
  templates/      Jinja2 화면
```

- 의존 방향: routes → services → core, services → models. core는 DB를 모른다.
- 채점·가중치·보기 생성은 core/quiz.py의 순수 함수다. 테스트가 DB 없이 돈다.
- 라우트는 세션을 `get_db_session` 의존성으로 받는다. 요청마다 열고 응답 뒤에 닫는다.

## 3. 주요 요청 흐름

### 3.1 단어 CSV 가져오기 (VOCA-FR-003)

1. `POST /wordbooks/{id}/import` (multipart 파일)
2. 라우트가 최대 20MB까지 바이트로 읽는다
3. `import_words_from_csv`: UTF-8 BOM 처리, 머리글 건너뜀, 중복·형식 오류 행 집계, 한 번에 커밋
4. 결과 개수를 쿼리 `notice`로 실어 단어장 화면으로 돌아간다

### 3.2 시험 (VOCA-FR-021~026)

1. `GET /wordbooks/{id}/test`: 옵션 화면
2. `POST /wordbooks/{id}/test`: `build_test_questions`가 가중치로 단어를 고르고 문항을 만든다. 정답은 화면에 싣지 않는다
3. `POST /wordbooks/{id}/test/grade`: 제출된 답을 `grade_test_answers`가 DB의 단어·뜻으로 다시 채점하고 `quiz_answers`에 기록한다
4. 점수와 틀린 문항(내 답·정답)을 보여 준다

### 3.3 통계 (VOCA-FR-031~034)

`GET /stats`: `stats_service`가 두 기록 테이블에서 정답률, 학습 일수, 단어장별 정답률, 자주 틀린 단어 상위 5개를 계산한다.

## 4. 오류 처리

- `ValidationError`, `DuplicateWordError`: 이전 화면으로 돌아가 오류 문구를 보여 준다
- `NotFoundError`: 목록 화면으로 돌아간다
- 입력 검증은 서비스 계층(`core/validation.py`)에서 한다. 화면의 `maxlength`는 보조 수단이다

## 5. 배포 구성

```
[학교 서버 프록시 /2026/voca-<학번>/]  --(주소 앞부분 제거·링크 재작성)-->  [컨테이너 0.0.0.0:8080]
                                                                          └─ /data/voca.db (볼륨)
```

- 앱은 `/` 기준으로 만든다. 템플릿의 링크와 폼 주소는 모두 `/`로 시작하는 따옴표 있는 경로다 (R-04)
- 설정은 환경변수로 받는다: `DB_PATH` (기본 `data/smart_voca.db`, 이미지에서는 `/data/voca.db`)
- 이미지는 `python:3.12-slim`, 의존성은 빌드 때 설치, 실행 중 인터넷 불필요 (R-07)
- 쓰기는 `/data`(DB)와 `/tmp`에만 한다. CSV는 메모리에서 처리한다

## 6. 테스트 구성

| 파일 | 범위 |
|---|---|
| tests/test_quiz.py | 출제 규칙, 채점, 시험 화면 흐름, 검색, 자주 틀린 단어 |
| tests/test_word_import.py | CSV 가져오기 규칙과 업로드 화면 |
| tests/test_routes.py | 단어장·단어·학습·결과 흐름 |
| tests/test_services.py, test_stats.py, test_scheduler.py, test_validation.py, test_config.py | 업무 규칙, 통계, 복습 간격, 검증, 설정 |

- 실행: 프로젝트 루트에서 `python -m unittest discover -s tests -v` (또는 pytest)
- 현재 결과: 70개 통과 (2026-11-25)

## 7. 알려진 한계

- 시험 제출값(정답 여부 판단용 OX 후보 등)은 화면의 숨은 값으로 되돌아온다. 1인 로컬 사용 전제라 허용했다. 공개 서비스로 바꾸면 서버에서 후보를 다시 만들어야 한다.
- 로그인, 다른 계정 이력, 설정은 없다 (도전 기능 미구현).
- 일차별 학습 세트(VOCA-FR-011)는 아직 없다. 현재 암기는 간격 복습 방식이다.

# 스마트보카

단어장을 만들고, 단어를 외우고, 정해진 간격으로 복습하는 1인용 웹 단어 학습 도구입니다.

- 기술 스택: Python 3.12, FastAPI, SQLAlchemy, Jinja2, SQLite (로그인 없음)
- 요구사항: `docs/smart-voca_Requirement_Spec_v1.0_261111.md`
- 기능 분해: `docs/smart-voca_Function_Map_v1.0_261111.md`

## 설치

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 실행

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.app:create_app --factory --port 8000
```

브라우저에서 `http://127.0.0.1:8000` 을 엽니다. 처음 실행하면 `data/smart_voca.db` 가 자동으로 만들어집니다.

DB 위치를 바꾸려면 프로젝트 루트에 `.env` 파일을 만들고 `DB_PATH` 를 설정합니다. 예시는 `.env.example` 을 참고하세요.
`.env` 는 `.gitignore` 대상이라 커밋되지 않습니다. 이미 설정된 셸 환경변수가 있으면 그 값이 우선합니다.

## 고른 DB

SQLite 한 파일(`DB_PATH`)을 씁니다. PostgreSQL은 쓰지 않습니다. 테이블은 처음 실행할 때 자동으로 만들어집니다.

## 과제 요구사항 구현 현황 (VOCA-FR)

- **구현**: VOCA-FR-001 (직접 입력 등록), 002 (목록·수정·삭제), 003 (CSV 일괄 등록, 같은 단어장의 중복은 건너뜀), 004 (영단어·뜻 검색), 021 (문제 수 지정), 022 (가중치 출제: 처음 보거나 자주 틀린 단어를 더 자주 냄), 023 (영→한·한→영·섞기), 024 (단답형·4지선다·OX), 025 (점수와 틀린 문항·정답), 026 (문항별 형식·방향·정오·시각을 DB에 저장), 033 (자주 틀린 단어 상위 5개), 034 (통계는 DB 이력으로 계산)
- **일부 구현**: VOCA-FR-012 (단어 카드 학습), 014 (답 기록 저장, 일차 정보는 없음), 031 (정답률과 학습 일수만 보임, 일차별 진도 없음), 032 (전체 정답률만 보임, 회차별 추이 없음)
- **미구현**: VOCA-FR-011 (일차별 학습 세트), 013 (전날 단어·자주 틀린 단어 섞기), 041~043 (로그인), 051~053 (다른 계정 이력), 061~062 (설정)

## 배포 (학교 서버, Docker)

`Dockerfile` 한 개로 이미지를 만듭니다. 컨테이너는 `0.0.0.0:8080` 에서 듣고, UID 10001로 실행하며, DB는 `/data/voca.db` 에 둡니다.

```powershell
docker build -t voca-app .
```

서버 점검 워크플로는 `.github/workflows/docker-check.yml` 입니다. 이 파일은 학과 제공본이라 고치지 않습니다.

## 테스트

프로젝트 루트에서 실행합니다.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## 디렉토리

```
src/
  app.py            FastAPI 앱 조립 (create_app)
  core/             순수 로직: 복습 스케줄, 통계, 입력 검증, 설정, 날짜
  models/           SQLAlchemy 모델과 DB 세션
  services/         업무 규칙 (단어장, 단어, 학습, 복습, 통계)
  routes/           HTTP 라우트 (화면 요청 처리)
  templates/        Jinja2 화면 템플릿
tests/              unittest 테스트
```

## 복습 간격

정답이 이어지면 1 → 3 → 7 → 14 → 30일 간격으로 늘어나고, 오답이면 1일 뒤로 되돌아갑니다.
간격 값은 `src/core/config.py` 의 상수입니다. 간격 방식은 기획 확정 전 임시 값입니다.

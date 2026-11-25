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

- **구현**: VOCA-FR-001 (직접 입력 등록), VOCA-FR-002 (목록·수정·삭제), VOCA-FR-003 (CSV 일괄 등록, 같은 단어장의 중복은 건너뜀), VOCA-FR-034 (통계는 DB 이력으로 계산)
- **일부 구현**: VOCA-FR-012 (단어 카드 학습), VOCA-FR-014·026 (답한 기록을 DB에 저장, 일차·출제 방향·형식은 아직 없음), VOCA-FR-031·032 (정답률 통계, 일차 현황은 아직 없음)
- **미구현**: VOCA-FR-004, 011, 013, 021~025, 033, 041~043, 051~053, 061~062

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

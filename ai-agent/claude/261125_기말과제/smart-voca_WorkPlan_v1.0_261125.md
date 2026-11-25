# 기말과제 작업계획 및 1차 제출 체크리스트

**파일 위치**: `ai-agent/claude/261125_기말과제/smart-voca_WorkPlan_v1.0_261125.md`
**작성일**: 2026-11-25
**버전**: v1.0
**설명**: 과제 공지(v1.1) 요약, 1차 제출(11-30) 체크리스트, 확인이 필요한 항목 정리

---

## 1. 과제 요약 (출처: `ai-agent/upload/01_공지 (1).md`, v1.1)

- 수업 단어장 프로그램을 **웹 앱**으로 재구현하고, 학교 서버(`/2026/voca-<학번>/`)에 올려 실행합니다.
- 기능: 단어 등록, 암기, 시험, 학습 진척 통계. 이력은 **DB**에 저장합니다.
- 제출: **GitHub 공개(Public) 리포** 하나. 루트에 `Dockerfile`, `.github/workflows/docker-check.yml`, `README.md`를 둡니다.
- 평가: 기능(서버 시연, 코드, DB) / 문서(`docs/`, `CLAUDE.md`, 커밋 이력) / 배포(서버 빌드·실행, 점검 워크플로 통과) / 계정 관리.
- 기본 기능과 제출 요건을 모두 채워야 만점입니다. 도전 기능(로그인, 다른 계정 이력 보기, 설정)은 가산점이며 기본을 대신하지 못합니다.
- DB는 **SQLite**입니다. PostgreSQL은 11-30까지 교수에게 말해 허락을 받아야 합니다.

## 2. 일정

| 날짜 | 할 일 | 상태 |
|---|---|---|
| 11-25 (수) | 과제 공지, 1차 제출 시작 | 진행 중 |
| 11-30 (월) 23:59 | **1차 제출 마감** (미완성 가능, 서버 사전 빌드용) | 미정 |
| 12-01 ~ 12-02 | 서버 사전 점검 결과 통보 | — |
| 12-01 ~ 12-11 (금) 23:59 | **최종 제출** (마감 시점 폼 값이 최종본) | — |
| 12-07 ~ 12-11 | 기말평가 시연 | — |

## 3. 1차 제출 체크리스트 (공지 §0)

- [ ] **1. 공개 GitHub 리포** 확인 또는 생성 (현재 `origin` = `https://github.com/won20221006-source/smart-voca.git`, 공개 여부 미확인)
- [ ] **2. 리포 뼈대 업로드**: `README.md`, `CLAUDE.md`(있음), `docs/` 기획서(`기획_yymmdd_제목 v0.1.md` 규칙 확인 필요), 첫 화면 앱 코드
- [ ] **3. `Dockerfile` 작성** (「Dockerfile 생성 프롬프트」 사용, 루트에 `.dockerignore`·`.gitattributes` 함께) — **원문 미확보**
- [ ] **4. `.github/workflows/docker-check.yml`** 원본을 수정 없이 배치 — **원문 미확보**
- [ ] **5. push 후 Actions 초록불 확인** (빨강이면 로그를 보고 수정)
- [ ] **6. 시크릿 창에서 리포 주소 접근 확인** (404면 Settings → Change visibility → Public)
- [ ] **7. 초록불 커밋의 SHA 40자**를 제출 폼에 기록 (리포 URL, SHA, 앱 이름 30자 이내, 한 줄 설명 80자 이내)

## 4. 확보가 필요한 자료 (공지가 참조하지만 업로드되지 않음)

- 소프트웨어 요건 (요구사항 ID `VOCA-FR-001` 등, §4.1~4.5 제출 요건 및 계정 자가 신고)
- Dockerfile 구성 (필수 규칙 R-01~R-10, 3.1 / 4.1~4.3 / 5. Windows 문제)
- Dockerfile 생성 프롬프트 (공통 프롬프트 + 스택별 추가문)
- `docker-check.yml` 원본

이 자료들이 있어야 Requirement_Spec과 Dockerfile 작업을 진행할 수 있습니다.

## 5. 확인이 필요한 사항

1. 리포 공개 여부 및 `origin`이 과제 제출용 리포와 같은지
2. 기획서(`docs/`) 이름 규칙: 공지는 `기획_yymmdd_제목 v0.1.md`, 프로젝트 방법론은 `{Project_Name}_{EN_Name}_vX.X_YYMMDD.md`. 어느 쪽을 따를지
3. 학교 서버 주소의 `<학번>`은 리포·문서에 적지 않고 제출 폼에만 입력 (`CLAUDE.md` 개인정보 규칙)
4. 스택: `CLAUDE.md` 기준 FastAPI + Jinja2 + SQLAlchemy + SQLite. 과제 허용 범위 내이며 Dockerfile 규칙 확인 후 확정

## 6. 다음 작업

1. 나머지 4개 자료 확보 → Requirement_Spec 요구사항 ID 매핑
2. Dockerfile 및 `.dockerignore` 작성 (Windows 로컬 빌드는 Docker 환경 확인 후)
3. 첫 화면 앱 코드와 `README.md` 작성
4. 커밋 (승인 후) → push → Actions 확인

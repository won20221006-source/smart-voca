# 작업 일지 (2026-11-11)

**파일 위치**: `ai-agent/claude/smart-voca_Journal_v1.0_261111.md`
**작성일**: 2026-11-11
**버전**: v1.0
**설명**: GitHub 리포지토리 연동 및 초기 커밋 작업 기록

---

## 깃 리포지토리 생성 요청 확인
요청: 여기 깃헙 리포지토리가 있는지 확인
처리: 프로젝트 디렉토리에 `.git`이 없고 원격도 없음을 확인. 생성 방식(로컬 초기화 / 신규 GitHub 생성 / 기존 리포 연결) 3가지를 제시.

## 리포지토리 생성 및 커밋 준비
요청: 깃헙 리포지토리 만들고 커밋할 수 있게 도와줘
처리:
- `git init -b main`으로 로컬 리포지토리 초기화
- `.gitignore` 작성 (`.env` 제외, `.env.example`만 커밋 대상. DB·캐시·`data/raw/`·`logs/`·`backups/` 제외)
- `gh auth status` 확인 → 미로그인 상태로 GitHub 리포 생성 보류

## 초기 로컬 커밋
요청: 진행해줘
처리: GitHub 미연결 상태에서 로컬 커밋까지만 진행
- `e99ffd3` chore: .gitignore 추가 (.env, DB, 캐시 제외)
- `e0f20ac` docs: 프로젝트 지침 및 초기 설계 문서 추가
- 커밋 메시지에 `Co-Authored-By: Claude Haiku 5.5 <noreply@anthropic.com>` 포함

## GitHub 리포 생성 시도 (실패)
요청: 로그인했어 / 연동 방법 / a로 부탁해 / 커밋 푸쉬해줘
처리:
- `gh auth status` 여러 차례 확인 → 이 세션에서 로그인 미반영 (`You are not logged into any GitHub hosts`)
- `%APPDATA%\GitHub CLI` 인증 정보 없음 확인
- `gh repo create` 미실행, `git remote` 미등록 → push 불가
- 대안 제시: (1) 이 세션에서 `! gh auth login` 후 재요청, (2) 웹에서 비공개 리포 생성 후 주소 전달

## 리포지토리 연동 완료
요청: 로그인했어 / 커밋 푸쉬해줘 / 네 (일지 반영 후 커밋·푸시 승인)
처리:
- GitHub 로그인 확인 (계정 `won20221006-source`, keyring 저장)
- `gh repo create smart-voca --private --source=. --remote=origin --push` 실행
- 원격: https://github.com/won20221006-source/smart-voca (비공개)
- `main` 브랜치 push 완료, `origin/main` 추적 설정
- 이 일지 파일도 커밋·push (승인 후)

## 남은 항목
- [ ] `docs/` 승격 대상 여부 검토 (현재 `docs/`에 Claude가 생성한 파일 없음)
- [ ] `README.md`, `src/` 등 다음 작업 착수 시 커밋 단위 분리

## 메모
- 이 일지 파일은 CLAUDE.md 기록 규칙에 따라 `ai-agent/claude/`에 작성했습니다.
- 세션 중 개별 항목의 정확한 시각은 기록하지 않았습니다(작성 시점 기준 15:34).
- 커밋 작성자는 현재 git 전역 설정값을 따릅니다.

## 연동 상태 재확인 (2026-11-18)
요청: 깃허브 연동 이어서 진행
처리:
- `gh auth status`: 계정 `won20221006-source` 로그인 유지 (scope: repo, workflow 등)
- `gh repo view`: `smart-voca` 비공개 리포 정상 조회
- `git fetch` 및 `git ls-remote`: 로컬·원격 `main` 모두 `5d98e19`로 일치, 미push 커밋 없음
- 작업 트리 clean 확인

## 핵심 로직 1차 구현 (2026-11-18)
요청: 계속 진행해줘
처리:
- 다음 단계를 기능 분해도(F4·F6·F8)의 순수 로직 모듈로 한정 (DB·웹은 패키지 설치 승인 후)
- 구현: `src/core/{errors,clock,config,validation,scheduler,stats}.py`, `src/__init__.py`, `src/core/__init__.py`
- 테스트: `tests/test_{scheduler,stats,validation}.py` (unittest, 표준 라이브러리만 사용)
- 매핑: REQ-001·005·006·010·015~018·022~024, F4.1~F4.3, F6.1~F6.3, F8.2·F8.5·F8.6 (주석에 REQ-ID 기재)
- 검증 한계: 이 환경에 실행 가능한 Python이 없음 (`python`은 스토어 실행 스텁). 테스트 미실행, 기댓값은 코드 읽기로 대조함
- 가정 2건 (요구사항 확인 필요): 새 단어는 추가한 날 복습 대상 / 예문 길이 제한 없음
- 미결 유지: 복습 간격 값(REQ-017 제안값을 config에 임시 적용), 로그인(REQ-025~026)
- 커밋·푸시는 미실행 (승인 대기)

## 웹 MVP 구현 및 실행 검증 (2026-11-18)
요청: 다 해줘 (Python 설치·테스트·커밋·푸시·나머지 구현)
처리:
- Python 3.12.10 설치(winget), 프로젝트 `.venv` 생성 후 패키지 설치 (requirements.txt 고정)
- 1차 핵심 로직 커밋·푸시: `7372361 feat: 복습 스케줄·학습 통계·입력 검증 핵심 로직 추가`
- DB 계층: `src/models/` (단어장·단어·학습기록, FK CASCADE, PRAGMA foreign_keys) (NFR-002, NFR-009)
- 서비스 계층: `src/services/` (단어장·단어·학습·복습·통계) 
- 웹 계층: `src/app.py`, `src/routes/`, `src/templates/` (단어장·단어·학습 카드·결과·오늘의 복습·통계)
- 테스트: `tests/test_services.py`, `tests/test_routes.py` 포함 전체 42건 통과
- 서버 실행 검증: uvicorn `src.app:create_app --factory` 기동, GET / 200, POST /wordbooks 303 후 목록 반영 확인 (임시 DB 사용)
- README.md, .env.example 작성 (NFR-001)
- 결정: 로그인 없음(REQ-025), 복습 간격은 REQ-017 제안값을 임시 적용, 새 단어 첫 복습일은 추가한 날 (가정, 확인 필요)
- 미해결: .env 자동 로드 미구현, Starlette TestClient의 httpx 관련 deprecation 경고 (동작 영향 없음)

## 미결 사항 정리 및 마무리 (2026-11-18)
요청: 알아서 다 해줘
처리:
- 복습 간격: 고정 간격 유지, 로그인 없음, 학습 방식 정답/오답, 새 단어 첫 복습일 = 추가일로 확정 → Decision_Records §6 기록
- `.env` 자동 로드 구현 (`src/core/config.py`, 표준 라이브러리만 사용), 테스트 `tests/test_config.py`
- 전체 unittest 46건 통과
- 실서버 학습 흐름 확인: 단어장 생성 → 단어 추가 → 학습 카드 → 정답/오답 → 결과 50% → 통계 반영 (임시 DB)
- httpx2 전환 시도: 패키지 설치가 권한 정책으로 거부되어 수행하지 않음. Starlette 경고는 동작에 영향 없음, 현재 httpx 유지
- 브라우저 클릭 테스트는 미수행 (HTTP 수준 검증까지)
- docs/ 승격은 미수행 (CLAUDE.md상 사용자 확인 필요)

## 할 수 있는 검증 수행 (2026-11-18)
요청: 할 수 있는 거 다 해줘
처리:
- 성능(NFR-003): 단어 1,000개 상세 화면 중앙값 14.7 ms, 최대 32.4 ms (`ai-agent/scripts/261118-단어목록성능측정.py`)
- 브라우저 렌더링: Edge 헤드리스로 목록·상세·학습 카드·복습·통계 화면 캡처 확인 (임시 파일, 저장소 밖)
- 요구사항 명세 §5 확인 항목 3건을 MVP 기준으로 확정 기록
- 미수행: 브라우저 클릭 조작 테스트 (헤드리스 캡처만 수행), docs/ 승격 (CLAUDE.md상 사용자 확인 필요), httpx2 전환 (설치 권한 거부)

## 승인 항목 처리: docs 승격, httpx2 전환 (2026-11-18)
요청: 그것도 다 오케이, 계속해줘
처리:
- httpx2==2.16.2 설치 (앞서 권한 거부 → 사용자 승인 후 재시도). 테스트 46건 통과, TestClient 경고 제거. requirements.txt에서 httpx 대체
- docs 승격 (git mv): Requirement_Spec, Function_Map, Decision_Records. 헤더 파일 위치 및 승인 상태 갱신
- 프로젝트 헌장(Project_Charter)은 승인자 "미정", 가정 포함 초안이라 승격하지 않음. 승인 확인 후 승격 필요
- 참조 경로 갱신: CLAUDE.md, README.md, 프로젝트 헌장
- 미수행: 브라우저 클릭 피드백 (사용자 입력 필요)

## 프로젝트 헌장 승인 및 docs 승격 (2026-11-18)
요청: 승인해주고 독스도 올려줘
처리:
- 프로젝트 헌장 승인 처리 (승인자: 사용자, 2026-11-18). 가정 항목 `[가정]`은 그대로 유지
- `git mv`로 `docs/smart-voca_Project_Charter_v1.0_261021.md` 로 이동, 헤더 갱신
- docs/ 산출물 4종: Project_Charter, Requirement_Spec, Function_Map, Decision_Records

## 2026-11-25 14:13 — 기말과제 공지 정리
요청: 업로드된 과제 공지 파일 정리 (교수 지시: 완성)
처리: `ai-agent/upload/01_공지 (1).md` 읽고 `ai-agent/claude/261125_기말과제/smart-voca_WorkPlan_v1.0_261125.md` 작성 (과제 요약, 일정, 1차 제출 체크리스트, 미확보 자료, 확인 사항). 공지가 참조하는 요건서·Dockerfile 규칙·프롬프트·docker-check.yml 원문은 업로드되지 않아 미확보로 기록. `docs/`는 건드리지 않음.

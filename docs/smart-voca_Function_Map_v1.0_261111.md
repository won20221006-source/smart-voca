# 스마트보카 기능 분해도 (Function Map)

**파일 위치**: `ai-agent/claude/smart-voca_Function_Map_v1.0_261111.md`
**작성일**: 2026-11-11
**버전**: v1.0 (초안, 승인 전)
**설명**: 요구사항 명세서(REQ-001~028, NFR-001~009)를 원자 단위 기능(F-ID)으로 계층 분해하고, 계획 모듈 위치와 추적 관계를 정의하는 설계 산출물

---

## 0. 전제

- 기술 스택: Python 3, FastAPI, SQLAlchemy, Jinja2/HTMX, SQLite (`Decision_Records_v1.0_261111.md` 확정)
- 요구사항 근거: `Requirement_Spec_v1.0_261111.md`
- 모듈 경로는 **계획**이며 아직 코드가 없다. 구현 시 변경될 수 있다.
- 원자 기능은 "한 번의 사용자 행위 또는 한 개의 규칙"으로 쪼갰다.
- 순수 계산 로직(F4, F6)은 웹 계층과 분리하여 단위 테스트한다 (NFR-007).

---

## 1. 계층 구조 (Tree)

```
스마트보카 (Level 0)
├── F1  단어장 관리
│   ├── F1.1  단어장 생성
│   ├── F1.2  단어장 목록 조회 (단어 수 포함)
│   ├── F1.3  단어장 이름 수정
│   └── F1.4  단어장 삭제 (소속 데이터 연쇄 삭제)
├── F2  단어 관리
│   ├── F2.1  단어·뜻 추가
│   ├── F2.2  예문 입력·저장
│   ├── F2.3  단어 목록 조회
│   ├── F2.4  단어 수정
│   ├── F2.5  단어 삭제
│   └── F2.6  중복 단어 검사
├── F3  학습 세션
│   ├── F3.1  세션 생성 (대상 단어 목록 구성)
│   ├── F3.2  카드 제시·뒤집기
│   ├── F3.3  정답/오답 입력
│   ├── F3.4  학습 이력 저장
│   └── F3.5  세션 결과 요약
├── F4  복습 스케줄러  [순수 로직]
│   ├── F4.1  다음 복습일 계산
│   ├── F4.2  복습 간격 규칙 로드
│   ├── F4.3  스케줄 계산기 인터페이스 (알고리즘 교체 지점)
│   └── F4.4  단어별 복습 일정 저장
├── F5  오늘의 복습
│   ├── F5.1  복습 대상 조회
│   ├── F5.2  단어장별 그룹화
│   ├── F5.3  복습 세션 시작 (F3.1 재사용)
│   └── F5.4  빈 상태 안내
├── F6  학습 통계  [순수 로직]
│   ├── F6.1  전체 정답률 계산
│   ├── F6.2  학습 일수 계산
│   └── F6.3  단어장별 정답률 계산
├── F7  사용자 구분
│   └── F7.1  단일 사용자 기본 모드 (로그인 없음)
└── F8  공통 기반
    ├── F8.1  DB 연결·테이블 초기화
    ├── F8.2  입력값 검증 (길이·필수 항목)
    ├── F8.3  환경설정 로드 (.env)
    ├── F8.4  공통 화면 레이아웃
    ├── F8.5  오류·안내 메시지 처리
    └── F8.6  날짜 처리 (로컬 시간대 기준 "오늘" 판단)
```

---

## 2. 원자 기능 목록

| F-ID | 기능 | 상위 | 연결 REQ / NFR | 계획 위치 (구현 시) | 비고 |
|------|------|------|----------------|--------------------|------|
| F1.1 | 단어장 생성 | F1 | REQ-001 | `src/routes/wordbook.py`, `src/services/wordbook_service.py` | |
| F1.2 | 단어장 목록 조회 | F1 | REQ-002 | `src/routes/wordbook.py`, `src/services/wordbook_service.py` | 단어 수 집계 |
| F1.3 | 단어장 이름 수정 | F1 | REQ-003 | `src/routes/wordbook.py`, `src/services/wordbook_service.py` | |
| F1.4 | 단어장 삭제 | F1 | REQ-004, NFR-009 | `src/services/wordbook_service.py`, `src/models/` | 삭제 전 확인 창, FK CASCADE |
| F2.1 | 단어·뜻 추가 | F2 | REQ-005, REQ-027 | `src/routes/word.py`, `src/services/word_service.py` | 사용자 직접 입력 |
| F2.2 | 예문 입력·저장 | F2 | REQ-006, REQ-027 | `src/services/word_service.py` | 선택 항목 |
| F2.3 | 단어 목록 조회 | F2 | REQ-007, NFR-003 | `src/routes/word.py`, `src/services/word_service.py` | 1,000개 규모 성능 기준 |
| F2.4 | 단어 수정 | F2 | REQ-008 | `src/services/word_service.py` | |
| F2.5 | 단어 삭제 | F2 | REQ-009 | `src/services/word_service.py` | 학습 이력도 삭제 |
| F2.6 | 중복 단어 검사 | F2 | REQ-010 | `src/services/word_service.py` | 대소문자·앞뒤 공백 무시 |
| F3.1 | 세션 생성 | F3 | REQ-011 | `src/services/study_service.py` | F5.3이 재사용 |
| F3.2 | 카드 제시·뒤집기 | F3 | REQ-012 | `src/routes/study.py`, `src/templates/study/` | HTMX 부분 갱신 |
| F3.3 | 정답/오답 입력 | F3 | REQ-013 | `src/routes/study.py`, `src/services/study_service.py` | |
| F3.4 | 학습 이력 저장 | F3 | REQ-015 | `src/services/study_service.py`, `src/models/` | 일시, 정답 여부 |
| F3.5 | 세션 결과 요약 | F3 | REQ-014 | `src/services/study_service.py`, `src/templates/study/` | |
| F4.1 | 다음 복습일 계산 | F4 | REQ-016, NFR-007 | `src/core/scheduler.py` | 순수 함수 |
| F4.2 | 복습 간격 규칙 로드 | F4 | REQ-017, NFR-004 | `src/core/config.py`, `.env.example` | 제안값 상수, §5 대기 |
| F4.3 | 스케줄 계산기 인터페이스 | F4 | REQ-018 | `src/core/scheduler.py` | 계산기를 주입받는 구조 |
| F4.4 | 단어별 복습 일정 저장 | F4 | REQ-016 | `src/models/`, `src/services/study_service.py` | 다음 복습일 컬럼 |
| F5.1 | 복습 대상 조회 | F5 | REQ-019 | `src/services/review_service.py` | 다음 복습일 ≤ 오늘 |
| F5.2 | 단어장별 그룹화 | F5 | REQ-019 | `src/services/review_service.py` | |
| F5.3 | 복습 세션 시작 | F5 | REQ-020 | `src/routes/review.py`, `src/services/study_service.py` | F3.1 재사용 |
| F5.4 | 빈 상태 안내 | F5 | REQ-021 | `src/templates/review/` | |
| F6.1 | 전체 정답률 계산 | F6 | REQ-022, NFR-007 | `src/core/stats.py` | 순수 함수 |
| F6.2 | 학습 일수 계산 | F6 | REQ-023, NFR-007 | `src/core/stats.py` | 서로 다른 날짜 수 |
| F6.3 | 단어장별 정답률 계산 | F6 | REQ-024 | `src/core/stats.py` | |
| F7.1 | 단일 사용자 기본 모드 | F7 | REQ-025 | `src/core/config.py` | 로그인 없음. REQ-026 보류 |
| F8.1 | DB 연결·테이블 초기화 | F8 | NFR-002 | `src/models/database.py` | SQLite 파일 1개 |
| F8.2 | 입력값 검증 | F8 | REQ-001, REQ-005, NFR-005 | `src/core/validation.py` | 길이·필수, 개인정보 필드 없음 |
| F8.3 | 환경설정 로드 | F8 | NFR-004 | `src/core/config.py` | `.env` 읽기 |
| F8.4 | 공통 화면 레이아웃 | F8 | NFR-006 | `src/templates/base.html` | 데스크톱 브라우저 기준 |
| F8.5 | 오류·안내 메시지 처리 | F8 | REQ-010, REQ-021 | `src/core/errors.py` | |
| F8.6 | 날짜 처리 | F8 | REQ-016, REQ-019, REQ-023 | `src/core/clock.py` | 시각을 주입 가능하게 분리 (테스트용) |

---

## 3. 요구사항 → 기능 역추적 (Coverage Check)

| REQ | 담당 F-ID | 상태 |
|-----|-----------|------|
| REQ-001 | F1.1, F8.2 | 매핑 완료 |
| REQ-002 | F1.2 | 매핑 완료 |
| REQ-003 | F1.3 | 매핑 완료 |
| REQ-004 | F1.4 | 매핑 완료 |
| REQ-005 | F2.1, F8.2 | 매핑 완료 |
| REQ-006 | F2.2 | 매핑 완료 |
| REQ-007 | F2.3 | 매핑 완료 |
| REQ-008 | F2.4 | 매핑 완료 |
| REQ-009 | F2.5 | 매핑 완료 |
| REQ-010 | F2.6, F8.5 | 매핑 완료 |
| REQ-011 | F3.1 | 매핑 완료 |
| REQ-012 | F3.2 | 매핑 완료 |
| REQ-013 | F3.3 | 매핑 완료 |
| REQ-014 | F3.5 | 매핑 완료 |
| REQ-015 | F3.4 | 매핑 완료 |
| REQ-016 | F4.1, F4.4, F8.6 | 매핑 완료 |
| REQ-017 | F4.2 | 매핑 완료 (값은 §5 대기) |
| REQ-018 | F4.3 | 매핑 완료 |
| REQ-019 | F5.1, F5.2, F8.6 | 매핑 완료 |
| REQ-020 | F5.3 | 매핑 완료 |
| REQ-021 | F5.4, F8.5 | 매핑 완료 |
| REQ-022 | F6.1 | 매핑 완료 |
| REQ-023 | F6.2, F8.6 | 매핑 완료 |
| REQ-024 | F6.3 | 매핑 완료 |
| REQ-025 | F7.1 | 매핑 완료 |
| REQ-026 | — | 보류 (§9-5 대기) |
| REQ-027 | F2.1, F2.2 | 매핑 완료 |
| REQ-028 | — | 보류 (MVP 제외) |

**NFR 매핑**: NFR-001→F8.3 및 실행 절차(README 예정), NFR-002→F8.1, NFR-003→F2.3, NFR-004→F4.2·F8.3, NFR-005→F8.2, NFR-006→F8.4, NFR-007→F4.*·F6.*, NFR-008→전체(구현 시 주석·테스트에 REQ-ID 기재), NFR-009→F1.4.

**결과**: 활성 REQ 25개 전부 매핑됨. 보류 REQ(026, 028)는 매핑하지 않음.

---

## 4. 설계 판단 메모

1. **F4·F6을 순수 로직으로 분리한 이유**: 간격 규칙이 아직 확정되지 않았으므로(§9-4), 계산 로직을 웹과 DB에서 떼어 두면 알고리즘 교체 시 화면 코드를 건드리지 않는다. (F4.3)
2. **F5.3이 F3.1을 재사용하는 이유**: 복습 세션과 일반 학습 세션의 차이는 "대상 목록"뿐이므로 세션 생성 로직을 하나로 둔다.
3. **F8.6 시각 주입**: "오늘" 판단을 테스트에서 고정하기 위해 현재 시각을 함수 인자로 받는다.

---

## 5. 확인 필요

1. 복습 간격 제안값(F4.2)과 알고리즘 방식 (기획서 §9-4)
2. 로그인 필요 여부 (기획서 §9-5). 필요해지면 F7.x 추가와 F8 인증 기능 신설

---

## 변경 이력

| 버전 | 일자 | 내용 |
|------|------|------|
| v1.0 | 2026-11-11 | 요구사항 명세서 기반 기능 분해 초안 작성 (F1~F8, 원자 기능 33개) |

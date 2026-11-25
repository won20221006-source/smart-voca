# 데이터 설계서

**파일 위치**: `ai-agent/claude/261125_기말과제/smart-voca_Data_Design_v1.0_261125.md`
**작성일**: 2026-11-25
**버전**: v1.0
**설명**: SQLite 테이블 정의, 관계, 인덱스와 과제 요구사항(VOCA-SUB-015) 대응. 실제 정의는 `src/models/entities.py`

---

## 1. 개요

- DB: SQLite 한 파일 (`DB_PATH`, 서버에서는 `/data/voca.db`)
- 테이블은 앱 시작 시 `Base.metadata.create_all`로 자동 생성된다 (VOCA-NFR-003)
- 외래키 CASCADE가 동작하도록 연결마다 `PRAGMA foreign_keys=ON`을 켠다
- 로그인이 없어 사용자 테이블은 없다 (도전 기능 미구현)

## 2. ERD (텍스트)

```
wordbooks 1 ──< words 1 ──< study_records
                        └──< quiz_answers
```

- 단어장 삭제 → 소속 단어 삭제 → 해당 학습 기록·시험 기록 삭제 (CASCADE)

## 3. 테이블 정의

### 3.1 wordbooks (단어장)

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | INTEGER | PK | 단어장 번호 |
| name | VARCHAR(50) | NOT NULL | 단어장 이름 (REQ-001) |
| created_at | DATETIME | NOT NULL, 기본값 현재 시각 | 만든 시각 |

### 3.2 words (단어)

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | INTEGER | PK | 단어 번호 |
| wordbook_id | INTEGER | FK → wordbooks.id, ON DELETE CASCADE, 인덱스 | 소속 단어장 |
| word | VARCHAR(100) | NOT NULL | 영단어 (최대 100자) |
| meaning | VARCHAR(200) | NOT NULL | 뜻 (최대 200자) |
| example | TEXT | NULL 허용 | 예문 (선택) |
| review_stage | INTEGER | NOT NULL, 기본값 0 | 복습 간격 단계 (0~4) |
| next_review_date | DATE | NOT NULL, 인덱스 | 다음 복습일 |
| created_at | DATETIME | NOT NULL, 기본값 현재 시각 | 추가 시각 |

- 같은 단어장 안의 중복 금지는 DB 제약이 아니라 서비스 계층에서 검사한다 (대소문자·앞뒤 공백 무시, `normalize_word_key`).
- CSV 일괄 등록도 같은 기준을 쓴다. 중복 행은 건너뛴다 (VOCA-FR-003).

### 3.3 study_records (암기 기록)

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | INTEGER | PK | 기록 번호 |
| word_id | INTEGER | FK → words.id, ON DELETE CASCADE, 인덱스 | 대상 단어 |
| is_correct | BOOLEAN | NOT NULL | 정답 여부 |
| studied_at | DATETIME | NOT NULL | 답한 시각 |
| studied_on | DATE | NOT NULL, 인덱스 | 학습한 날짜 (통계의 날짜 기준) |

### 3.4 quiz_answers (시험 문항 기록)

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | INTEGER | PK | 기록 번호 |
| word_id | INTEGER | FK → words.id, ON DELETE CASCADE, 인덱스 | 출제된 단어 |
| question_format | VARCHAR(10) | NOT NULL | `short` / `choice` / `ox` |
| direction | VARCHAR(10) | NOT NULL | `en_ko` / `ko_en` (섞기는 문항마다 확정된 방향을 저장) |
| is_correct | BOOLEAN | NOT NULL | 정오 |
| answered_at | DATETIME | NOT NULL | 답한 시각 |
| answered_on | DATE | NOT NULL, 인덱스 | 답한 날짜 |

- `study_records`와 분리한 이유: 시험 기록에는 형식·방향이 필요하고, 암기 기록에는 없다. 기존 테이블을 바꾸지 않으면 기존 DB를 그대로 쓸 수 있다.

## 4. 통계 계산 규칙 (VOCA-FR-034)

- 화면에 값을 저장하지 않는다. 통계는 매번 `study_records`와 `quiz_answers`에서 계산한다.
- 전체 정답률, 학습 일수, 단어장별 정답률: `study_records` 기준 (`stats_service`).
- 자주 틀린 단어: 두 기록 테이블의 오답 수를 합산해 상위 5개 (`get_top_missed_words`).
- 시험 출제 가중치: 두 기록 테이블을 합쳐 본 적 여부, 틀린 횟수, 마지막 학습일을 계산한다 (`load_word_history`).

## 5. 복습 상태 (review_stage)

- 단계 0~4는 `src/core/config.py`의 `REVIEW_INTERVAL_DAYS = (1, 3, 7, 14, 30)`에 대응한다.
- 정답이면 다음 단계, 오답이면 단계 0으로 되돌리고 1일 뒤에 다시 본다.
- 시험(`quiz_answers`)은 복습 상태를 바꾸지 않는다. 시험 결과는 출제 가중치에만 쓴다.

## 6. 과제 요구사항 대응 (VOCA-SUB-015)

| 과제 요구 | 테이블 |
|---|---|
| 단어 (VOCA-NFR-002) | words |
| 암기 이력 (VOCA-FR-014) | study_records |
| 시험 이력 (VOCA-FR-026) | quiz_answers |
| 단어장 | wordbooks |
| 사용자·설정 (도전, VOCA-NFR-002) | 미구현 |

## 7. 확인 항목

- `example`이 NULL 허용인 이유: 예문은 선택 입력이다 (REQ-006).
- 인덱스는 날짜 기준 통계와 단어 기준 조회에 쓰이는 컬럼에만 둔다.
- 운영 중 스키마 변경 시 `create_all`은 기존 테이블을 바꾸지 않는다. 컬럼을 추가하려면 마이그레이션이 필요하다 (현재 범위 밖).

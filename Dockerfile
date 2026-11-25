# syntax 지시어는 쓰지 않는다 (서버 빌드 규칙 R-10)
# 2026-11-25 - smart-voca - 학교 서버 배포용 이미지 (UID 10001, 8080 포트, /data SQLite)
# 파일 위치: Dockerfile

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DB_PATH=/data/voca.db

WORKDIR /app

# 사용자 생성 후 DB 디렉터리를 만든다. 쓰기는 /data 와 /tmp 에만 한다 (R-05, R-06)
RUN groupadd --gid 10001 app \
 && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin app \
 && mkdir -p /data \
 && chown 10001:10001 /data

# 의존성을 먼저 설치해 캐시를 살린다 (R-13). 실행 중 인터넷은 필요 없다 (R-07)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

USER 10001:10001

EXPOSE 8080

# 운영용 서버로 실행한다 (R-03, R-14). 앱은 / 기준으로 만든다 (R-04)
CMD ["uvicorn", "src.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers", "--forwarded-allow-ips", "*"]

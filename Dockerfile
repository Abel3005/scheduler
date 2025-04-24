# 1. 베이스 이미지
FROM python:3.11-slim

# PostgreSQL 클라이언트 및 개발 패키지 설치
RUN apt-get update && apt-get install -y postgresql-client libpq-dev && rm -rf /var/lib/apt/lists/*

# 2. 작업 디렉토리
WORKDIR /app

# 3. 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 앱 소스 복사 -> 호스트 파일 사용으로 변경
VOLUME ["/app"]

# 5. 포트 지정 & 실행
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

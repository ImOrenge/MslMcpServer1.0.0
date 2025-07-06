# MSL MCP Server - Optimized for Smithery
FROM python:3.11-slim

# 작업 디렉토리
WORKDIR /app

# 의존성 파일 복사 및 설치 (캐시 최적화)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 환경변수
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 포트 노출
EXPOSE 8000

# 헬스체크
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# HTTP 서버 실행
CMD ["python", "simple_http_server.py"]

# 메타데이터
LABEL maintainer="ImOrenge"
LABEL version="1.0.0"
LABEL description="MSL MCP Server - Gaming Macro Scripting Language with AI"
LABEL repository="https://github.com/ImOrenge/MslMcpServer1.0.0" 
# MSL MCP Server - Optimized for Smithery
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 최소화 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Python 패키지 요구사항 먼저 설치 (캐시 최적화)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 환경변수 설정
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 불필요한 파일 제거
RUN find . -name "*.pyc" -delete \
    && find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# 비root 사용자 생성 (보안)
RUN groupadd -r msluser && useradd -r -g msluser msluser \
    && chown -R msluser:msluser /app
USER msluser

# 헬스체크 (간단하게)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=2 \
    CMD python -c "import msl.msl_lexer; print('OK')" || exit 1

# 기본 명령어
CMD ["python", "server.py"]

# 메타데이터
LABEL maintainer="ImOrenge"
LABEL version="1.0.0"
LABEL description="MSL MCP Server - Gaming Macro Scripting Language with AI"
LABEL repository="https://github.com/ImOrenge/MslMcpServer1.0.0" 
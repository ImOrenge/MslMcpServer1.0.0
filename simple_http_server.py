#!/usr/bin/env python3
"""
MSL MCP HTTP Server - Smithery 배포용 간단한 HTTP 서버

기본 MCP 기능과 헬스체크 엔드포인트를 제공합니다.
"""

import asyncio
import json
import logging
from aiohttp import web, web_request
from msl.msl_lexer import MSLLexer
from msl.msl_parser import MSLParser

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("msl-http-server")

class MSLHttpServer:
    """MSL MCP HTTP 서버 클래스"""
    
    def __init__(self):
        self.app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        """HTTP 라우트 설정"""
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_post('/parse', self.parse_msl)
        self.app.router.add_post('/validate', self.validate_msl)
        self.app.router.add_get('/examples', self.get_examples)
        self.app.router.add_get('/', self.root)
    
    async def health_check(self, request):
        """헬스체크 엔드포인트"""
        return web.json_response({
            "status": "healthy",
            "service": "MSL MCP Server",
            "version": "1.0.0"
        })
    
    async def root(self, request):
        """루트 엔드포인트 - 서버 정보 제공"""
        return web.json_response({
            "name": "MSL MCP Server",
            "version": "1.0.0",
            "description": "Macro Scripting Language MCP Server",
            "endpoints": [
                "/health - Health check",
                "/parse - Parse MSL script",
                "/validate - Validate MSL script", 
                "/examples - Get MSL examples"
            ]
        })
    
    async def parse_msl(self, request):
        """MSL 스크립트 파싱 엔드포인트"""
        try:
            data = await request.json()
            script = data.get('script', '')
            
            if not script:
                return web.json_response({
                    "error": "스크립트가 제공되지 않았습니다"
                }, status=400)
            
            # MSL 렉서로 토큰화
            lexer = MSLLexer(script)
            tokens = lexer.tokenize()
            
            # 기본 파싱 정보
            result = {
                "script": script,
                "token_count": len(tokens),
                "tokens": [{"type": token.type.value, "value": token.value} for token in tokens[:10]],  # 처음 10개만
                "analysis": {
                    "estimated_time": self.calculate_execution_time(tokens),
                    "complexity": self.calculate_complexity(tokens),
                    "key_count": len([t for t in tokens if t.type.value in ['KEY', 'MOUSE_BUTTON']])
                }
            }
            
            return web.json_response(result)
            
        except Exception as e:
            logger.error(f"파싱 오류: {e}")
            return web.json_response({
                "error": f"파싱 중 오류 발생: {str(e)}"
            }, status=500)
    
    async def validate_msl(self, request):
        """MSL 스크립트 검증 엔드포인트"""
        try:
            data = await request.json()
            script = data.get('script', '')
            
            if not script:
                return web.json_response({
                    "error": "스크립트가 제공되지 않았습니다"
                }, status=400)
            
            # 기본 검증
            lexer = MSLLexer(script)
            tokens = lexer.tokenize()
            
            errors = []
            warnings = []
            
            # 간단한 검증 로직
            if len(tokens) == 0:
                errors.append("빈 스크립트입니다")
            
            execution_time = self.calculate_execution_time(tokens)
            if execution_time > 10000:
                warnings.append(f"실행 시간이 {execution_time}ms로 매우 깁니다")
            
            result = {
                "script": script,
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "token_count": len(tokens)
            }
            
            return web.json_response(result)
            
        except Exception as e:
            logger.error(f"검증 오류: {e}")
            return web.json_response({
                "error": f"검증 중 오류 발생: {str(e)}"
            }, status=500)
    
    async def get_examples(self, request):
        """MSL 예제 제공 엔드포인트"""
        examples = [
            {
                "title": "기본 키 입력",
                "script": "W",
                "description": "W키 한 번 누르기"
            },
            {
                "title": "순차 실행",
                "script": "W,A,S,D",
                "description": "W, A, S, D 키를 순서대로 누르기"
            },
            {
                "title": "동시 실행",
                "script": "Ctrl+C",
                "description": "Ctrl과 C키를 동시에 누르기"
            },
            {
                "title": "지연 포함",
                "script": "W,(500),A",
                "description": "W키 누르고 500ms 후 A키 누르기"
            },
            {
                "title": "반복 실행",
                "script": "Space*3",
                "description": "스페이스바 3번 연속 누르기"
            }
        ]
        
        return web.json_response({
            "examples": examples,
            "count": len(examples)
        })
    
    def calculate_execution_time(self, tokens):
        """토큰 기반 실행 시간 계산"""
        total_time = 0
        for token in tokens:
            if token.type.value == 'DELAY':
                total_time += int(token.value) if token.value.isdigit() else 0
            elif token.type.value in ['KEY', 'MOUSE_BUTTON']:
                total_time += 50  # 기본 키 입력 시간
        return total_time
    
    def calculate_complexity(self, tokens):
        """토큰 기반 복잡도 계산 (1-10)"""
        complexity = 1
        operator_count = len([t for t in tokens if t.type.value in ['COMMA', 'PLUS', 'REPEAT']])
        complexity += min(operator_count * 0.5, 4)
        return min(int(complexity), 10)

async def create_app():
    """애플리케이션 생성"""
    server = MSLHttpServer()
    return server.app

async def main():
    """서버 시작"""
    logger.info("MSL HTTP Server 시작 중...")
    
    app = await create_app()
    
    # 서버 실행
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()
    
    logger.info("서버가 http://0.0.0.0:8000 에서 실행 중입니다")
    logger.info("헬스체크: http://0.0.0.0:8000/health")
    
    # 서버 계속 실행
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("서버 종료 중...")
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 
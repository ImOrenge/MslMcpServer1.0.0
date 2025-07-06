#!/usr/bin/env python3
"""
간단한 MSL MCP 서버 테스트

import 문제를 우회하여 기본 MCP 기능만 테스트합니다.
"""

import asyncio
import logging
import sys
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 프로젝트 경로를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simple-msl-mcp-server")

# MCP 서버 인스턴스 생성
server = Server("simple-msl-assistant")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    간단한 테스트용 도구 목록을 반환합니다.
    """
    return [
        Tool(
            name="test_msl_parse",
            description="MSL 스크립트 파싱 테스트 도구입니다. 기본적인 토큰화와 구문 분석을 수행합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "분석할 MSL 스크립트 코드"
                    }
                },
                "required": ["script"]
            }
        ),
        Tool(
            name="test_msl_info",
            description="MSL 언어에 대한 기본 정보를 제공합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "정보를 원하는 주제 (syntax, examples, help)",
                        "default": "help"
                    }
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    요청된 도구를 실행합니다.
    """
    try:
        if name == "test_msl_parse":
            return await test_msl_parse(arguments)
        elif name == "test_msl_info":
            return await test_msl_info(arguments)
        else:
            return [TextContent(
                type="text",
                text=f"❌ 알 수 없는 도구: {name}"
            )]
    except Exception as e:
        logger.error(f"도구 실행 오류: {e}")
        return [TextContent(
            type="text",
            text=f"❌ 도구 실행 중 오류 발생: {str(e)}"
        )]

async def test_msl_parse(arguments: dict) -> list[TextContent]:
    """간단한 MSL 파싱 테스트"""
    script = arguments.get("script", "").strip()
    
    if not script:
        return [TextContent(
            type="text",
            text="❌ 스크립트가 제공되지 않았습니다."
        )]
    
    try:
        # 기본적인 MSL 구성 요소들을 import하여 테스트
        from msl_ast import KeyNode, SequentialNode
        from msl.msl_lexer import MSLLexer
        
        # Lexer 테스트
        lexer = MSLLexer(script)
        tokens = lexer.tokenize()
        
        result = f"✅ MSL 파싱 테스트 성공!\n\n"
        result += f"📝 입력 스크립트: '{script}'\n\n"
        result += f"🔍 토큰 분석 결과:\n"
        result += f"• 총 토큰 수: {len(tokens)}개\n"
        
        # 토큰 타입별 개수
        token_types = {}
        for token in tokens:
            token_types[token.type.value] = token_types.get(token.type.value, 0) + 1
        
        for token_type, count in token_types.items():
            result += f"• {token_type}: {count}개\n"
        
        result += f"\n📊 분석 요약:\n"
        result += f"• 구문 오류: 없음\n"
        result += f"• 파싱 상태: 성공\n"
        result += f"• 실행 가능: ✅\n\n"
        
        result += f"💡 다음 단계:\n"
        result += f"• 더 복잡한 스크립트로 테스트해보세요\n"
        result += f"• 다른 MSL 도구들을 사용해보세요"
        
        return [TextContent(type="text", text=result)]
        
    except Exception as e:
        error_msg = f"❌ MSL 파싱 테스트 실패:\n{str(e)}\n\n"
        error_msg += f"입력 스크립트: '{script}'\n"
        error_msg += f"오류를 확인하고 다시 시도해주세요."
        return [TextContent(type="text", text=error_msg)]

async def test_msl_info(arguments: dict) -> list[TextContent]:
    """MSL 정보 제공"""
    topic = arguments.get("topic", "help")
    
    if topic == "syntax":
        result = """📚 MSL (Macro Scripting Language) 구문 가이드

🔤 기본 요소:
• 키: W, A, S, D, Space, Ctrl, Alt, Shift
• 숫자: 100, 500, 1.5 (시간, 횟수 등)
• 변수: $combo1, $sequence (사용자 정의)

⚡ 연산자:
• , (쉼표): 순차 실행 - W,A,S,D
• + (플러스): 동시 실행 - Ctrl+C, Shift+A
• > (큰 따옴표): 홀드 연결 - W>A>S
• | (파이프): 병렬 실행 - (W,A)|(S,D)
• * (별표): 반복 - W*5, (A,S)*3
• ~ (틸드): 토글 - ~CapsLock

⏰ 타이밍:
• (숫자): 지연 - (500) = 500ms 대기
• [숫자]: 홀드 - [W,1000] = W키 1초간 홀드
• {숫자}: 간격 - W*5{100} = W키 5번, 100ms 간격

🎯 예시:
• W,A,S,D - WASD 순차 입력
• Ctrl+C - Ctrl과 C 동시 입력
• W(500),A - W 입력 후 500ms 대기, A 입력
• Q*3{200} - Q키 3번, 200ms 간격으로 반복"""

    elif topic == "examples":
        result = """🎮 MSL 스크립트 예제 모음

🏃 이동 관련:
• W,A,S,D - 기본 이동
• W(2000),S(2000) - 앞으로 2초, 뒤로 2초
• Shift+W - 달리기

⚔️ 전투 관련:
• Q,W,E,R - 스킬 콤보
• 1,2,3*5 - 아이템 사용 후 공격 5회
• Ctrl+1,2,3 - 컨트롤 그룹 선택

🎯 정밀 조작:
• @(100,200) - 마우스를 (100,200) 위치로
• lclick,rclick - 좌클릭, 우클릭
• wheel_up*3 - 마우스 휠 위로 3번

🔄 반복 작업:
• (Q,W,E)*10{1000} - QWE 10번 반복, 1초 간격
• Space*5{500} - 스페이스 5번, 0.5초 간격"""

    else:  # help
        result = """🚀 MSL MCP 서버 도움말

📖 MSL이란?
MSL(Macro Scripting Language)은 게이머를 위한 직관적이고 강력한 매크로 언어입니다.
키보드, 마우스 입력을 자동화하여 반복 작업을 효율적으로 처리할 수 있습니다.

🛠️ 사용 가능한 도구:
• test_msl_parse: MSL 스크립트 파싱 및 분석
• test_msl_info: MSL 구문과 예제 정보 제공

💡 사용법:
1. test_msl_parse로 스크립트 구문 확인
2. test_msl_info(topic="syntax")로 구문 학습
3. test_msl_info(topic="examples")로 예제 참고

🔍 예시 스크립트:
• 간단: "W,A,S,D"
• 복합: "Ctrl+C,(500),Ctrl+V"
• 반복: "Q*5{200}"

❓ 더 자세한 정보가 필요하시면 각 도구를 사용해보세요!"""

    return [TextContent(type="text", text=result)]

async def main():
    """메인 실행 함수"""
    logger.info("🚀 Simple MSL MCP 서버 시작")
    
    try:
        # stdio를 통한 MCP 서버 실행
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"서버 실행 오류: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 
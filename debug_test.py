#!/usr/bin/env python3
"""
MCP 서버 디버깅 테스트
"""

import sys
import os

# 프로젝트 경로를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """모든 import가 정상적으로 작동하는지 테스트"""
    print("🔍 Import 테스트 시작")
    print("=" * 50)
    
    try:
        print("1. MCP 라이브러리 import...")
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import Tool, TextContent
        print("   ✅ MCP 라이브러리 성공")
        
        print("2. MSL AST import...")
        from msl_ast import KeyNode, SequentialNode
        print("   ✅ MSL AST 성공")
        
        print("3. MSL Lexer import...")
        from msl.msl_lexer import MSLLexer
        print("   ✅ MSL Lexer 성공")
        
        print("4. 간단한 MCP 서버 import...")
        import simple_mcp_server
        print("   ✅ 간단한 MCP 서버 성공")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Import 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_msl_basic():
    """MSL 기본 기능 테스트"""
    print("\n🔧 MSL 기본 기능 테스트")
    print("=" * 50)
    
    try:
        from msl.msl_lexer import MSLLexer
        
        # 간단한 스크립트 테스트
        test_scripts = [
            "W",
            "W,A",
            "Ctrl+C",
            "W(500)"
        ]
        
        for script in test_scripts:
            try:
                lexer = MSLLexer(script)
                tokens = lexer.tokenize()
                print(f"   ✅ '{script}' → {len(tokens)}개 토큰")
            except Exception as e:
                print(f"   ❌ '{script}' → 오류: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ MSL 테스트 실패: {e}")
        return False

def test_server_creation():
    """MCP 서버 생성 테스트"""
    print("\n🚀 MCP 서버 생성 테스트")
    print("=" * 50)
    
    try:
        from mcp.server import Server
        
        # 서버 인스턴스 생성
        server = Server("test-server")
        print("   ✅ MCP 서버 인스턴스 생성 성공")
        
        # 간단한 도구 정의 테스트
        @server.list_tools()
        async def list_tools():
            from mcp.types import Tool
            return [
                Tool(
                    name="test_tool",
                    description="테스트 도구",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "input": {"type": "string"}
                        }
                    }
                )
            ]
        
        print("   ✅ 도구 정의 성공")
        
        @server.call_tool()
        async def call_tool(name: str, arguments: dict):
            from mcp.types import TextContent
            return [TextContent(type="text", text="테스트 성공")]
        
        print("   ✅ 도구 호출 핸들러 정의 성공")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 서버 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 MSL MCP 서버 디버깅 테스트")
    print("=" * 60)
    
    results = []
    
    # 각 테스트 실행
    results.append(("Import 테스트", test_imports()))
    results.append(("MSL 기본 기능", test_msl_basic()))
    results.append(("서버 생성", test_server_creation()))
    
    # 결과 요약
    print("\n📊 테스트 결과 요약")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n총 {passed}/{len(results)}개 테스트 통과")
    
    if passed == len(results):
        print("\n🎉 모든 기본 테스트가 통과했습니다!")
        print("💡 MCP 서버가 정상적으로 작동할 준비가 되었습니다.")
    else:
        print("\n⚠️ 일부 테스트가 실패했습니다.")
        print("💡 문제를 해결한 후 다시 시도해주세요.")

if __name__ == "__main__":
    main() 
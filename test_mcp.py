#!/usr/bin/env python3
"""
MSL MCP 서버 테스트 스크립트

이 스크립트는 MSL MCP 서버의 기본 기능들을 테스트합니다:
1. 파싱 기능 테스트
2. 검증 기능 테스트  
3. 예제 생성 테스트
4. 설명 기능 테스트
"""

import asyncio
import sys
import os
import traceback

# 프로젝트 경로를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.parse_tool import ParseMSLTool
from tools.validate_tool import ValidateMSLTool
from tools.examples_tool import ExamplesMSLTool
from tools.explain_tool import ExplainMSLTool


async def test_parse_tool():
    """파싱 도구 테스트"""
    print("🔍 MSL 파싱 도구 테스트")
    print("=" * 50)
    
    parse_tool = ParseMSLTool()
    
    # 테스트 케이스들
    test_cases = [
        "W,A,S,D",  # 순차 실행
        "Ctrl+C",   # 동시 실행
        "Q*3",      # 반복
        "W(500),A", # 지연 포함
        "invalid_syntax!!!",  # 오류 케이스
    ]
    
    for i, script in enumerate(test_cases, 1):
        print(f"\n테스트 {i}: '{script}'")
        try:
            result = await parse_tool.execute({"script": script})
            print(f"✅ 성공: {result[0].text[:100]}...")
        except Exception as e:
            print(f"❌ 오류: {str(e)}")
    
    print("\n" + "=" * 50)


async def test_validate_tool():
    """검증 도구 테스트"""
    print("🔍 MSL 검증 도구 테스트")
    print("=" * 50)
    
    validate_tool = ValidateMSLTool()
    
    # 테스트 케이스들
    test_cases = [
        "W,A,S,D",        # 정상 케이스
        "Ctrl+C,Ctrl+V",  # 정상 케이스
        "Q*999",          # 성능 이슈 케이스
        "invalid!!!",     # 오류 케이스
    ]
    
    for i, script in enumerate(test_cases, 1):
        print(f"\n테스트 {i}: '{script}'")
        try:
            result = await validate_tool.execute({"script": script})
            print(f"✅ 성공: {result[0].text[:100]}...")
        except Exception as e:
            print(f"❌ 오류: {str(e)}")
    
    print("\n" + "=" * 50)


async def test_examples_tool():
    """예제 도구 테스트"""
    print("🔍 MSL 예제 도구 테스트")
    print("=" * 50)
    
    examples_tool = ExamplesMSLTool()
    
    # 테스트 케이스들
    test_cases = [
        {"category": "combat"},
        {"category": "movement"},
        {"game_type": "fps"},
        {"count": 3},
    ]
    
    for i, args in enumerate(test_cases, 1):
        print(f"\n테스트 {i}: {args}")
        try:
            result = await examples_tool.execute(args)
            print(f"✅ 성공: {result[0].text[:100]}...")
        except Exception as e:
            print(f"❌ 오류: {str(e)}")
    
    print("\n" + "=" * 50)


async def test_explain_tool():
    """설명 도구 테스트"""
    print("🔍 MSL 설명 도구 테스트")
    print("=" * 50)
    
    explain_tool = ExplainMSLTool()
    
    # 테스트 케이스들
    test_cases = [
        {"input": "W,A,S,D"},
        {"input": "Ctrl+C", "detail_level": "advanced"},
        {"input": "Q*3"},
        {"input": "W(500),A"},
    ]
    
    for i, args in enumerate(test_cases, 1):
        print(f"\n테스트 {i}: {args}")
        try:
            result = await explain_tool.execute(args)
            print(f"✅ 성공: {result[0].text[:100]}...")
        except Exception as e:
            print(f"❌ 오류: {str(e)}")
    
    print("\n" + "=" * 50)


async def main():
    """메인 테스트 함수"""
    print("🚀 MSL MCP 서버 기능 테스트 시작")
    print("=" * 70)
    
    try:
        # 각 도구별 테스트 실행
        await test_parse_tool()
        await test_validate_tool()
        await test_examples_tool()
        await test_explain_tool()
        
        print("\n🎉 모든 테스트 완료!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {str(e)}")
        print(f"스택 트레이스:\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    # 비동기 메인 함수 실행
    asyncio.run(main()) 
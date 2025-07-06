#!/usr/bin/env python3
"""
MSL MCP 서버 간단 테스트 스크립트

이 스크립트는 MSL의 기본 구성 요소들을 개별적으로 테스트합니다.
"""

import sys
import os

# 프로젝트 경로를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """기본 import 테스트"""
    print("🔍 기본 import 테스트")
    print("=" * 50)
    
    try:
        # MSL AST 클래스들 import 테스트
        from msl_ast import MSLNode, KeyNode, NumberNode, SequentialNode
        print("✅ MSL AST 클래스들 import 성공")
        
        # MSL Lexer import 테스트
        from msl.msl_lexer import MSLLexer, TokenType
        print("✅ MSL Lexer import 성공")
        
        # MSL Parser import 테스트
        from msl.msl_parser import MSLParser
        print("✅ MSL Parser import 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ Import 오류: {e}")
        return False

def test_lexer():
    """Lexer 기본 테스트"""
    print("\n🔍 MSL Lexer 테스트")
    print("=" * 50)
    
    try:
        from msl.msl_lexer import MSLLexer
        
        # 간단한 테스트 케이스들
        test_cases = [
            "W",           # 단일 키
            "W,A",         # 순차 실행
            "Ctrl+C",      # 동시 실행
            "W(500)",      # 지연 포함
        ]
        
        for script in test_cases:
            try:
                lexer = MSLLexer(script)  # 텍스트와 함께 초기화
                tokens = lexer.tokenize()  # 매개변수 없이 호출
                print(f"✅ '{script}' → {len(tokens)}개 토큰")
            except Exception as e:
                print(f"❌ '{script}' → 오류: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lexer 테스트 오류: {e}")
        return False

def test_parser():
    """Parser 기본 테스트"""
    print("\n🔍 MSL Parser 테스트")
    print("=" * 50)
    
    try:
        from msl.msl_parser import MSLParser
        parser = MSLParser()
        
        # 간단한 테스트 케이스들
        test_cases = [
            "W",           # 단일 키
            "W,A",         # 순차 실행
        ]
        
        for script in test_cases:
            try:
                ast = parser.parse(script)
                print(f"✅ '{script}' → AST 타입: {type(ast).__name__}")
            except Exception as e:
                print(f"❌ '{script}' → 파싱 오류: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Parser 테스트 오류: {e}")
        return False

def test_ast_creation():
    """AST 노드 생성 테스트"""
    print("\n🔍 AST 노드 생성 테스트")
    print("=" * 50)
    
    try:
        from msl_ast import KeyNode, NumberNode, SequentialNode
        
        # 키 노드 생성 테스트
        key_node = KeyNode("W")
        print(f"✅ KeyNode 생성: {key_node}")
        
        # 숫자 노드 생성 테스트
        num_node = NumberNode(500)
        print(f"✅ NumberNode 생성: {num_node}")
        
        # 순차 노드 생성 테스트
        seq_node = SequentialNode()
        seq_node.add_child(key_node)
        seq_node.add_child(num_node)
        print(f"✅ SequentialNode 생성: {seq_node} (자식 {len(seq_node.children)}개)")
        
        return True
        
    except Exception as e:
        print(f"❌ AST 생성 테스트 오류: {e}")
        return False

def main():
    """메인 테스트 실행 함수"""
    print("🚀 MSL MCP 서버 간단 테스트 시작")
    print("=" * 60)
    
    # 각 테스트 실행
    tests = [
        test_basic_imports,
        test_ast_creation,
        test_lexer,
        test_parser,
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} 실행 중 오류: {e}")
    
    # 결과 요약
    print("\n" + "=" * 60)
    print(f"📊 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 기본 테스트가 통과했습니다!")
        print("\n💡 다음 단계:")
        print("• MCP 서버 실행: py server.py")
        print("• 실제 MCP 클라이언트 연결 테스트")
    else:
        print("⚠️  일부 테스트가 실패했습니다. 오류를 확인해주세요.")
    
    return passed == total

if __name__ == "__main__":
    main() 
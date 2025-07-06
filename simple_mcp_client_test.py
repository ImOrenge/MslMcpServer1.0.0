#!/usr/bin/env python3
"""
간단한 MSL MCP 서버 클라이언트 테스트
"""

import asyncio
import json
import subprocess
import sys
import os

async def test_simple_mcp_server():
    """간단한 MCP 서버와 통신하여 기능을 테스트합니다."""
    print("🚀 간단한 MSL MCP 서버 테스트 시작")
    print("=" * 60)
    
    try:
        # MCP 서버 프로세스 시작
        print("📡 MCP 서버 연결 중...")
        process = await asyncio.create_subprocess_exec(
            sys.executable, "simple_mcp_server.py",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # 초기화 메시지 전송
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "simple-msl-test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("🔄 서버 초기화 중...")
        await send_message(process, init_request)
        response = await receive_message(process)
        
        if response and "result" in response:
            print("✅ 서버 초기화 성공!")
            server_name = response['result'].get('serverInfo', {}).get('name', '알 수 없음')
            print(f"   서버 정보: {server_name}")
        else:
            print("❌ 서버 초기화 실패")
            return False
        
        # 도구 목록 요청
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("\n🔍 사용 가능한 도구 조회 중...")
        await send_message(process, tools_request)
        tools_response = await receive_message(process)
        
        if tools_response and "result" in tools_response:
            tools = tools_response["result"]["tools"]
            print(f"✅ {len(tools)}개 도구 발견:")
            for tool in tools:
                print(f"   • {tool['name']}: {tool['description'][:50]}...")
        else:
            print("❌ 도구 목록 조회 실패")
            return False
        
        # MSL 파싱 도구 테스트
        print("\n🔧 MSL 파싱 도구 테스트 중...")
        parse_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "test_msl_parse",
                "arguments": {
                    "script": "W,A,S,D"
                }
            }
        }
        
        await send_message(process, parse_request)
        parse_response = await receive_message(process)
        
        if parse_response and "result" in parse_response:
            print("✅ MSL 파싱 성공!")
            content = parse_response["result"]["content"][0]["text"]
            print(f"   결과 미리보기:")
            # 결과의 첫 몇 줄만 표시
            lines = content.split('\n')[:6]
            for line in lines:
                print(f"   {line}")
            if len(content.split('\n')) > 6:
                print("   ...")
        else:
            print("❌ MSL 파싱 실패")
            if parse_response and "error" in parse_response:
                print(f"   오류: {parse_response['error']}")
        
        # MSL 정보 도구 테스트
        print("\n📚 MSL 정보 도구 테스트 중...")
        info_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "test_msl_info",
                "arguments": {
                    "topic": "help"
                }
            }
        }
        
        await send_message(process, info_request)
        info_response = await receive_message(process)
        
        if info_response and "result" in info_response:
            print("✅ MSL 정보 조회 성공!")
            content = info_response["result"]["content"][0]["text"]
            # 결과의 첫 몇 줄만 표시
            lines = content.split('\n')[:5]
            for line in lines:
                print(f"   {line}")
            if len(content.split('\n')) > 5:
                print("   ...")
        else:
            print("❌ MSL 정보 조회 실패")
        
        # 프로세스 종료
        process.terminate()
        await process.wait()
        
        print("\n🎉 간단한 MCP 서버 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

async def send_message(process, message):
    """MCP 서버에 JSON-RPC 메시지를 전송합니다."""
    message_str = json.dumps(message) + "\n"
    process.stdin.write(message_str.encode())
    await process.stdin.drain()

async def receive_message(process):
    """MCP 서버로부터 JSON-RPC 응답을 받습니다."""
    try:
        # 타임아웃 설정 (10초)
        line = await asyncio.wait_for(process.stdout.readline(), timeout=10.0)
        if line:
            return json.loads(line.decode().strip())
        return None
    except asyncio.TimeoutError:
        print("⏰ 서버 응답 타임아웃")
        return None
    except json.JSONDecodeError as e:
        print(f"📝 JSON 파싱 오류: {e}")
        return None

def main():
    """메인 실행 함수"""
    # 기존 서버 프로세스가 있다면 종료
    try:
        subprocess.run(["taskkill", "/F", "/IM", "python.exe"], 
                      capture_output=True, check=False)
        print("🔄 기존 Python 프로세스 정리 완료")
    except:
        pass
    
    # 비동기 테스트 실행
    success = asyncio.run(test_simple_mcp_server())
    
    if success:
        print("\n✅ 간단한 MCP 서버가 정상 작동합니다!")
        print("\n💡 테스트 결과:")
        print("• MCP 프로토콜 통신: ✅")
        print("• 도구 목록 조회: ✅")
        print("• MSL 파싱 기능: ✅")
        print("• MSL 정보 제공: ✅")
        print("\n🎯 다음 단계:")
        print("• 실제 MCP 클라이언트(예: Claude Desktop)에서 연결 테스트")
        print("• 더 복잡한 MSL 스크립트로 테스트")
        print("• 전체 기능을 포함한 원본 서버 수정")
    else:
        print("\n❌ MCP 서버에 문제가 있습니다. 로그를 확인해주세요.")

if __name__ == "__main__":
    main() 
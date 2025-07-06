/**
 * MSL (Macro Scripting Language) 토큰 타입 정의
 * 게이밍 매크로를 위한 스크립팅 언어의 기본 구조
 */

export enum TokenType {
  // 기본 키/버튼
  KEY = 'KEY',                    // 키보드 키 (A, B, C, ...)
  MOUSE_BUTTON = 'MOUSE_BUTTON',  // 마우스 버튼 (LMB, RMB, MMB)
  
  // 연산자
  COMMA = 'COMMA',                // , (순차 실행)
  PLUS = 'PLUS',                  // + (동시 실행) 
  PIPE = 'PIPE',                  // | (병렬 실행)
  HOLD = 'HOLD',                  // > (홀드)
  TOGGLE = 'TOGGLE',              // ~ (토글)
  REPEAT = 'REPEAT',              // * (반복)
  CONTINUOUS = 'CONTINUOUS',      // & (연속)
  
  // 타이밍 제어
  DELAY = 'DELAY',                // (ms) 지연
  HOLD_TIME = 'HOLD_TIME',        // [ms] 홀드 시간
  INTERVAL = 'INTERVAL',          // {ms} 간격
  FADE = 'FADE',                  // <ms> 페이드
  
  // 고급 기능
  VARIABLE = 'VARIABLE',          // $var 변수
  COORDINATE = 'COORDINATE',      // @(x,y) 마우스 좌표
  WHEEL = 'WHEEL',                // wheel+/- 마우스 휠
  
  // 구조
  LPAREN = 'LPAREN',              // (
  RPAREN = 'RPAREN',              // )
  LBRACKET = 'LBRACKET',          // [
  RBRACKET = 'RBRACKET',          // ]
  LBRACE = 'LBRACE',              // {
  RBRACE = 'RBRACE',              // }
  LANGLE = 'LANGLE',              // <
  RANGLE = 'RANGLE',              // >
  
  // 특수
  NUMBER = 'NUMBER',              // 숫자
  STRING = 'STRING',              // 문자열
  IDENTIFIER = 'IDENTIFIER',      // 식별자
  EOF = 'EOF',                    // 파일 끝
  NEWLINE = 'NEWLINE',           // 줄바꿈
  WHITESPACE = 'WHITESPACE'       // 공백
}

/**
 * MSL 토큰 인터페이스
 */
export interface Token {
  type: TokenType;
  value: string;
  line: number;
  column: number;
}

/**
 * MSL AST 노드 타입
 */
export interface ASTNode {
  type: string;
  value?: string | number;
  children?: ASTNode[];
  line?: number;
  column?: number;
}

/**
 * MSL 스크립트 실행 정보
 */
export interface ExecutionInfo {
  estimatedTime: number;    // 예상 실행 시간 (ms)
  complexity: number;       // 복잡도 점수 (1-10)
  keyCount: number;         // 총 키 입력 수
  hasAdvancedFeatures: boolean; // 고급 기능 사용 여부
}

/**
 * MSL 파싱 결과
 */
export interface ParseResult {
  ast: ASTNode;
  tokens: Token[];
  executionInfo: ExecutionInfo;
  errors: string[];
  warnings: string[];
} 
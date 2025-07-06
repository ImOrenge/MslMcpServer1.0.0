import { Token, TokenType } from './msl-types.js';

/**
 * MSL 렉서 클래스
 * MSL 스크립트를 토큰으로 분해하는 기능을 제공합니다.
 */
export class MSLLexer {
  private text: string;
  private position: number = 0;
  private line: number = 1;
  private column: number = 1;

  constructor(text: string) {
    this.text = text;
  }

  /**
   * 현재 문자를 반환합니다.
   */
  private currentChar(): string | null {
    if (this.position >= this.text.length) {
      return null;
    }
    return this.text[this.position];
  }

  /**
   * 다음 문자로 이동합니다.
   */
  private advance(): void {
    if (this.position < this.text.length && this.text[this.position] === '\n') {
      this.line++;
      this.column = 1;
    } else {
      this.column++;
    }
    this.position++;
  }

  /**
   * 앞을 내다봅니다 (peek).
   */
  private peek(offset: number = 1): string | null {
    const peekPos = this.position + offset;
    if (peekPos >= this.text.length) {
      return null;
    }
    return this.text[peekPos];
  }

  /**
   * 공백을 건너뜁니다.
   */
  private skipWhitespace(): void {
    while (this.currentChar() && /\s/.test(this.currentChar()!) && this.currentChar() !== '\n') {
      this.advance();
    }
  }

  /**
   * 숫자를 읽습니다.
   */
  private readNumber(): string {
    let result = '';
    while (this.currentChar() && /\d/.test(this.currentChar()!)) {
      result += this.currentChar();
      this.advance();
    }
    return result;
  }

  /**
   * 식별자(키 이름 등)를 읽습니다.
   */
  private readIdentifier(): string {
    let result = '';
    while (this.currentChar() && /[a-zA-Z0-9_]/.test(this.currentChar()!)) {
      result += this.currentChar();
      this.advance();
    }
    return result;
  }

  /**
   * 키 이름인지 확인합니다.
   */
  private isKeyName(identifier: string): boolean {
    const keyNames = [
      // 알파벳 키
      'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
      'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
      // 숫자 키
      '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
      // 특수 키
      'Space', 'Enter', 'Tab', 'Shift', 'Ctrl', 'Alt', 'Esc', 'F1', 'F2', 'F3', 'F4',
      'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'Up', 'Down', 'Left', 'Right',
      // 마우스
      'LMB', 'RMB', 'MMB', 'MB4', 'MB5'
    ];
    return keyNames.includes(identifier.toUpperCase());
  }

  /**
   * 다음 토큰을 가져옵니다.
   */
  public getNextToken(): Token {
    while (this.currentChar()) {
      const char = this.currentChar()!;
      const line = this.line;
      const column = this.column;

      // 공백 처리
      if (/\s/.test(char) && char !== '\n') {
        this.skipWhitespace();
        continue;
      }

      // 줄바꿈
      if (char === '\n') {
        this.advance();
        return { type: TokenType.NEWLINE, value: '\n', line, column };
      }

      // 연산자들
      switch (char) {
        case ',':
          this.advance();
          return { type: TokenType.COMMA, value: ',', line, column };
        case '+':
          this.advance();
          return { type: TokenType.PLUS, value: '+', line, column };
        case '|':
          this.advance();
          return { type: TokenType.PIPE, value: '|', line, column };
        case '>':
          this.advance();
          return { type: TokenType.HOLD, value: '>', line, column };
        case '~':
          this.advance();
          return { type: TokenType.TOGGLE, value: '~', line, column };
        case '*':
          this.advance();
          return { type: TokenType.REPEAT, value: '*', line, column };
        case '&':
          this.advance();
          return { type: TokenType.CONTINUOUS, value: '&', line, column };
      }

      // 괄호들
      switch (char) {
        case '(':
          this.advance();
          // 지연 시간 확인 - (숫자)
          if (this.currentChar() && /\d/.test(this.currentChar()!)) {
            const number = this.readNumber();
            if (this.currentChar() === ')') {
              this.advance();
              return { type: TokenType.DELAY, value: number, line, column };
            }
          }
          return { type: TokenType.LPAREN, value: '(', line, column };
        case ')':
          this.advance();
          return { type: TokenType.RPAREN, value: ')', line, column };
        case '[':
          this.advance();
          // 홀드 시간 확인 - [숫자]
          if (this.currentChar() && /\d/.test(this.currentChar()!)) {
            const number = this.readNumber();
            if (this.currentChar() === ']') {
              this.advance();
              return { type: TokenType.HOLD_TIME, value: number, line, column };
            }
          }
          return { type: TokenType.LBRACKET, value: '[', line, column };
        case ']':
          this.advance();
          return { type: TokenType.RBRACKET, value: ']', line, column };
        case '{':
          this.advance();
          // 간격 시간 확인 - {숫자}
          if (this.currentChar() && /\d/.test(this.currentChar()!)) {
            const number = this.readNumber();
            if (this.currentChar() === '}') {
              this.advance();
              return { type: TokenType.INTERVAL, value: number, line, column };
            }
          }
          return { type: TokenType.LBRACE, value: '{', line, column };
        case '}':
          this.advance();
          return { type: TokenType.RBRACE, value: '}', line, column };
        case '<':
          this.advance();
          // 페이드 시간 확인 - <숫자>
          if (this.currentChar() && /\d/.test(this.currentChar()!)) {
            const number = this.readNumber();
            if (this.currentChar() === '>') {
              this.advance();
              return { type: TokenType.FADE, value: number, line, column };
            }
          }
          return { type: TokenType.LANGLE, value: '<', line, column };
      }

      // 숫자
      if (/\d/.test(char)) {
        const number = this.readNumber();
        return { type: TokenType.NUMBER, value: number, line, column };
      }

      // 변수 ($var)
      if (char === '$') {
        this.advance();
        const identifier = this.readIdentifier();
        return { type: TokenType.VARIABLE, value: '$' + identifier, line, column };
      }

      // 좌표 (@(x,y))
      if (char === '@' && this.peek() === '(') {
        this.advance(); // @
        this.advance(); // (
        const x = this.readNumber();
        if (this.currentChar() === ',') {
          this.advance();
          const y = this.readNumber();
          if (this.currentChar() === ')') {
            this.advance();
            return { type: TokenType.COORDINATE, value: `@(${x},${y})`, line, column };
          }
        }
      }

      // 휠 (wheel+, wheel-)
      if (char === 'w' && this.text.substring(this.position, this.position + 5) === 'wheel') {
        this.position += 5;
        this.column += 5;
        const direction = this.currentChar();
        if (direction === '+' || direction === '-') {
          this.advance();
          return { type: TokenType.WHEEL, value: `wheel${direction}`, line, column };
        }
      }

      // 식별자 (키 이름 등)
      if (/[a-zA-Z]/.test(char)) {
        const identifier = this.readIdentifier();
        
        if (this.isKeyName(identifier)) {
          return { type: TokenType.KEY, value: identifier.toUpperCase(), line, column };
        } else {
          return { type: TokenType.IDENTIFIER, value: identifier, line, column };
        }
      }

      // 알 수 없는 문자
      this.advance();
    }

    // 파일 끝
    return { type: TokenType.EOF, value: '', line: this.line, column: this.column };
  }

  /**
   * 모든 토큰을 가져옵니다.
   */
  public getAllTokens(): Token[] {
    const tokens: Token[] = [];
    let token = this.getNextToken();
    
    while (token.type !== TokenType.EOF) {
      // 공백과 줄바꿈은 필터링
      if (token.type !== TokenType.WHITESPACE && token.type !== TokenType.NEWLINE) {
        tokens.push(token);
      }
      token = this.getNextToken();
    }
    
    tokens.push(token); // EOF 토큰 추가
    return tokens;
  }
} 
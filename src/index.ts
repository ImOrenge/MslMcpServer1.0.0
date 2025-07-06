import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { z } from 'zod';
import OpenAI from 'openai';
import { MSLLexer } from './msl-lexer.js';
import { TokenType, ParseResult, ExecutionInfo } from './msl-types.js';

/**
 * 설정 스키마 정의
 * Smithery에서 사용자가 설정할 수 있는 값들
 */
export const configSchema = z.object({
  openaiApiKey: z.string().describe("OpenAI API 키 (AI 기반 MSL 생성용)"),
  openaiModel: z.string().default("gpt-4o").describe("사용할 OpenAI 모델"),
  debug: z.boolean().default(false).describe("디버그 모드 활성화")
});

/**
 * MSL MCP 서버 메인 함수
 * TypeScript로 구현된 게이밍 매크로 스크립팅 언어 서버
 */
export default function ({ config }: { config: z.infer<typeof configSchema> }) {
  const server = new McpServer({
    name: 'MSL MCP Server (TypeScript)',
    version: '1.0.0'
  });

  // OpenAI 클라이언트 초기화
  const openai = new OpenAI({
    apiKey: config.openaiApiKey
  });

  /**
   * MSL 스크립트 파싱 도구
   * MSL 코드를 토큰으로 분석하고 구문 검증을 수행합니다.
   */
  server.tool(
    'parse_msl',
    'MSL 스크립트를 파싱하고 토큰 분석 결과를 반환합니다',
    {
      script: z.string().describe('분석할 MSL 스크립트'),
      includeTokens: z.boolean().default(true).describe('토큰 목록 포함 여부'),
      validateSyntax: z.boolean().default(true).describe('구문 검증 수행 여부')
    },
    async ({ script, includeTokens, validateSyntax }) => {
      try {
        // MSL 렉서로 토큰화
        const lexer = new MSLLexer(script);
        const tokens = lexer.getAllTokens();

        // 기본 실행 정보 계산
        const executionInfo: ExecutionInfo = {
          estimatedTime: calculateExecutionTime(tokens),
          complexity: calculateComplexity(tokens),
          keyCount: tokens.filter(t => t.type === TokenType.KEY || t.type === TokenType.MOUSE_BUTTON).length,
          hasAdvancedFeatures: tokens.some(t => 
            t.type === TokenType.VARIABLE || 
            t.type === TokenType.COORDINATE || 
            t.type === TokenType.WHEEL
          )
        };

        // 구문 검증
        const errors: string[] = [];
        const warnings: string[] = [];
        
        if (validateSyntax) {
          validateMSLSyntax(tokens, errors, warnings);
        }

        const result: ParseResult = {
          ast: { type: 'script', children: [] }, // 간단한 AST
          tokens: includeTokens ? tokens : [],
          executionInfo,
          errors,
          warnings
        };

        return {
          content: [{
            type: 'text',
            text: `✅ MSL 파싱 완료!

📊 **분석 결과:**
- 총 토큰 수: ${tokens.length}
- 키 입력 수: ${executionInfo.keyCount}
- 예상 실행 시간: ${executionInfo.estimatedTime}ms
- 복잡도: ${executionInfo.complexity}/10
- 고급 기능 사용: ${executionInfo.hasAdvancedFeatures ? '예' : '아니오'}

${errors.length > 0 ? `❌ **오류:**\n${errors.map(e => `- ${e}`).join('\n')}\n` : ''}
${warnings.length > 0 ? `⚠️ **경고:**\n${warnings.map(w => `- ${w}`).join('\n')}\n` : ''}

${includeTokens ? `🔍 **토큰 목록:**\n${tokens.slice(0, -1).map(t => `${t.type}: "${t.value}"`).join(', ')}` : ''}`
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: 'text',
            text: `❌ MSL 파싱 오류: ${error instanceof Error ? error.message : '알 수 없는 오류'}`
          }]
        };
      }
    }
  );

  /**
   * AI 기반 MSL 스크립트 생성 도구
   * 자연어 설명을 받아 MSL 스크립트를 자동 생성합니다.
   */
  server.tool(
    'generate_msl',
    '자연어 설명으로부터 MSL 스크립트를 AI로 생성합니다',
    {
      prompt: z.string().describe('생성할 매크로에 대한 자연어 설명'),
      gameContext: z.string().default('general').describe('게임 컨텍스트 (FPS, MMORPG, RTS 등)'),
      complexity: z.enum(['simple', 'medium', 'advanced']).default('medium').describe('생성할 스크립트의 복잡도')
    },
    async ({ prompt, gameContext, complexity }) => {
      try {
        const systemPrompt = `당신은 MSL (Macro Scripting Language) 전문가입니다. 
게이머를 위한 매크로 스크립트를 생성해주세요.

MSL 문법:
- 키: A, B, C, W, S, Space, Enter, LMB, RMB 등
- 순차 실행: , (쉼표)
- 동시 실행: + (플러스)
- 지연: (숫자) 예: (500) = 500ms 대기
- 홀드: [숫자] 예: [1000] = 1초 홀드
- 반복: * 예: W*3 = W키 3번
- 병렬: | 예: W|A = W와 A 병렬 실행

예시:
- "Q키 누르고 500ms 후 W키" → Q,(500),W
- "Shift와 W 동시에 누르기" → Shift+W
- "스페이스바 3번 연속" → Space*3

게임 컨텍스트: ${gameContext}
복잡도: ${complexity}`;

        const completion = await openai.chat.completions.create({
          model: config.openaiModel,
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: prompt }
          ],
          max_tokens: 500,
          temperature: 0.3
        });

        const generatedScript = completion.choices[0]?.message?.content?.trim() || '';
        
        // 생성된 스크립트 검증
        const lexer = new MSLLexer(generatedScript);
        const tokens = lexer.getAllTokens();
        const executionInfo = {
          estimatedTime: calculateExecutionTime(tokens),
          complexity: calculateComplexity(tokens),
          keyCount: tokens.filter(t => t.type === TokenType.KEY || t.type === TokenType.MOUSE_BUTTON).length,
          hasAdvancedFeatures: tokens.some(t => 
            t.type === TokenType.VARIABLE || 
            t.type === TokenType.COORDINATE || 
            t.type === TokenType.WHEEL
          )
        };

        return {
          content: [{
            type: 'text',
            text: `🤖 **AI 생성 MSL 스크립트:**

\`\`\`msl
${generatedScript}
\`\`\`

📊 **스크립트 정보:**
- 키 입력 수: ${executionInfo.keyCount}
- 예상 실행 시간: ${executionInfo.estimatedTime}ms
- 복잡도: ${executionInfo.complexity}/10
- 게임 컨텍스트: ${gameContext}

💡 **사용법:** 이 스크립트를 게임 매크로 프로그램에 복사해서 사용하세요!`
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: 'text',
            text: `❌ MSL 생성 오류: ${error instanceof Error ? error.message : '알 수 없는 오류'}\n\n💡 OpenAI API 키가 올바른지 확인해주세요.`
          }]
        };
      }
    }
  );

  /**
   * MSL 스크립트 검증 도구
   * 스크립트의 구문 오류와 잠재적 문제점을 찾아냅니다.
   */
  server.tool(
    'validate_msl',
    'MSL 스크립트의 구문과 안전성을 검증합니다',
    {
      script: z.string().describe('검증할 MSL 스크립트'),
      checkPerformance: z.boolean().default(true).describe('성능 문제 검사 여부'),
      checkSafety: z.boolean().default(true).describe('안전성 검사 여부')
    },
    async ({ script, checkPerformance, checkSafety }) => {
      try {
        const lexer = new MSLLexer(script);
        const tokens = lexer.getAllTokens();
        
        const errors: string[] = [];
        const warnings: string[] = [];
        const suggestions: string[] = [];

        // 기본 구문 검증
        validateMSLSyntax(tokens, errors, warnings);

        // 성능 검사
        if (checkPerformance) {
          const executionTime = calculateExecutionTime(tokens);
          if (executionTime > 10000) {
            warnings.push(`실행 시간이 ${executionTime}ms로 매우 깁니다. 최적화를 고려해보세요.`);
          }
          
          const repeatCount = tokens.filter(t => t.type === TokenType.REPEAT).length;
          if (repeatCount > 5) {
            suggestions.push('반복이 많습니다. 루프 최적화를 고려해보세요.');
          }
        }

        // 안전성 검사
        if (checkSafety) {
          const keyCount = tokens.filter(t => t.type === TokenType.KEY).length;
          if (keyCount > 50) {
            warnings.push('키 입력이 너무 많습니다. 게임에서 스팸으로 감지될 수 있습니다.');
          }
        }

        const status = errors.length === 0 ? '✅ 검증 통과' : '❌ 검증 실패';
        
        return {
          content: [{
            type: 'text',
            text: `${status}

📝 **검증 결과:**
- 총 토큰 수: ${tokens.length}
- 구문 오류: ${errors.length}개
- 경고: ${warnings.length}개
- 제안사항: ${suggestions.length}개

${errors.length > 0 ? `❌ **오류:**\n${errors.map(e => `- ${e}`).join('\n')}\n` : ''}
${warnings.length > 0 ? `⚠️ **경고:**\n${warnings.map(w => `- ${w}`).join('\n')}\n` : ''}
${suggestions.length > 0 ? `💡 **제안사항:**\n${suggestions.map(s => `- ${s}`).join('\n')}\n` : ''}

${errors.length === 0 ? '🎉 스크립트가 올바르게 작성되었습니다!' : '🔧 오류를 수정한 후 다시 시도해주세요.'}`
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: 'text',
            text: `❌ 검증 오류: ${error instanceof Error ? error.message : '알 수 없는 오류'}`
          }]
        };
      }
    }
  );

  /**
   * MSL 예제 제공 도구
   * 다양한 게임 상황별 MSL 스크립트 예제를 제공합니다.
   */
  server.tool(
    'msl_examples',
    '게임별, 난이도별 MSL 스크립트 예제를 제공합니다',
    {
      category: z.enum(['combat', 'movement', 'utility', 'combo']).default('combat').describe('예제 카테고리'),
      gameType: z.enum(['fps', 'mmorpg', 'rts', 'general']).default('general').describe('게임 타입'),
      difficulty: z.enum(['beginner', 'intermediate', 'advanced']).default('beginner').describe('난이도')
    },
    async ({ category, gameType, difficulty }) => {
      const examples = getMSLExamples(category, gameType, difficulty);
      
      return {
        content: [{
          type: 'text',
          text: `📚 **MSL 예제 모음**
카테고리: ${category} | 게임: ${gameType} | 난이도: ${difficulty}

${examples.map((example, index) => `
**${index + 1}. ${example.title}**
\`\`\`msl
${example.script}
\`\`\`
설명: ${example.description}
`).join('\n')}

💡 **팁:** 이 예제들을 참고해서 자신만의 매크로를 만들어보세요!`
        }]
      };
    }
  );

  return server.server;
}

/**
 * 실행 시간 계산 함수
 */
function calculateExecutionTime(tokens: any[]): number {
  let totalTime = 0;
  
  for (const token of tokens) {
    switch (token.type) {
      case TokenType.DELAY:
        totalTime += parseInt(token.value) || 0;
        break;
      case TokenType.HOLD_TIME:
        totalTime += parseInt(token.value) || 0;
        break;
      case TokenType.KEY:
      case TokenType.MOUSE_BUTTON:
        totalTime += 50; // 기본 키 입력 시간
        break;
    }
  }
  
  return totalTime;
}

/**
 * 복잡도 계산 함수 (1-10 스케일)
 */
function calculateComplexity(tokens: any[]): number {
  let complexity = 1;
  
  const operatorCount = tokens.filter(t => 
    [TokenType.PLUS, TokenType.PIPE, TokenType.REPEAT, TokenType.TOGGLE].includes(t.type)
  ).length;
  
  const advancedCount = tokens.filter(t =>
    [TokenType.VARIABLE, TokenType.COORDINATE, TokenType.WHEEL].includes(t.type)
  ).length;
  
  complexity += Math.min(operatorCount * 0.5, 4);
  complexity += Math.min(advancedCount * 2, 5);
  
  return Math.min(Math.round(complexity), 10);
}

/**
 * MSL 구문 검증 함수
 */
function validateMSLSyntax(tokens: any[], errors: string[], warnings: string[]): void {
  let parenCount = 0;
  let bracketCount = 0;
  let braceCount = 0;
  
  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i];
    
    switch (token.type) {
      case TokenType.LPAREN:
        parenCount++;
        break;
      case TokenType.RPAREN:
        parenCount--;
        if (parenCount < 0) {
          errors.push(`줄 ${token.line}: 닫는 괄호가 여는 괄호보다 많습니다`);
        }
        break;
      case TokenType.LBRACKET:
        bracketCount++;
        break;
      case TokenType.RBRACKET:
        bracketCount--;
        break;
      case TokenType.LBRACE:
        braceCount++;
        break;
      case TokenType.RBRACE:
        braceCount--;
        break;
    }
  }
  
  if (parenCount !== 0) {
    errors.push('괄호가 올바르게 닫히지 않았습니다');
  }
  if (bracketCount !== 0) {
    errors.push('대괄호가 올바르게 닫히지 않았습니다');
  }
  if (braceCount !== 0) {
    errors.push('중괄호가 올바르게 닫히지 않았습니다');
  }
}

/**
 * MSL 예제 데이터
 */
function getMSLExamples(category: string, gameType: string, difficulty: string) {
  const examples = {
    combat: {
      fps: {
        beginner: [
          {
            title: "기본 사격",
            script: "LMB",
            description: "왼쪽 마우스 버튼으로 사격"
          },
          {
            title: "연속 사격",
            script: "LMB*3",
            description: "3번 연속 사격"
          }
        ],
        intermediate: [
          {
            title: "리로드 콤보",
            script: "LMB*5,(100),R,(2000),LMB*5",
            description: "5발 사격 → 100ms 대기 → 리로드 → 2초 대기 → 다시 5발 사격"
          }
        ]
      },
      mmorpg: {
        beginner: [
          {
            title: "기본 공격",
            script: "Q",
            description: "Q키로 스킬 사용"
          },
          {
            title: "스킬 콤보",
            script: "Q,(500),W,(500),E",
            description: "Q → 0.5초 대기 → W → 0.5초 대기 → E"
          }
        ]
      }
    },
    movement: {
      general: {
        beginner: [
          {
            title: "앞으로 이동",
            script: "W[1000]",
            description: "W키를 1초간 홀드"
          },
          {
            title: "좌우 이동",
            script: "A[500],D[500]",
            description: "왼쪽으로 0.5초, 오른쪽으로 0.5초"
          }
        ]
      }
    }
  };
  
  return examples[category]?.[gameType]?.[difficulty] || examples[category]?.general?.[difficulty] || [
    {
      title: "기본 예제",
      script: "Space",
      description: "스페이스바 누르기"
    }
  ];
} 
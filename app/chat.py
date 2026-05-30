"""
자소서 첨삭 AI 대화 모듈

사용자와 자소서 첨삭 관련 대화를 주고받습니다.
essay_question / essay_answer / company 컨텍스트를 시스템 프롬프트에 포함합니다.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DEFAULT_MODEL = "openai/gpt-5.4-mini"

SYSTEM_PROMPT = """당신은 자기소개서 첨삭 전문가입니다. 사용자가 자소서 작성에 관해 질문하면 구체적이고 실용적인 조언을 제공하세요.

## 역할
- 사용자의 자소서에 대한 추가 피드백 및 수정 방향 제시
- 특정 문장·표현의 개선 방법 안내
- 직무·기업에 맞는 자소서 작성 전략 조언

## 언어 규칙
모든 답변은 반드시 **한국어**로 작성하세요.

## 답변 스타일
- 친절하고 전문적인 톤
- 구체적인 예시와 함께 설명
- 핵심 내용을 간결하게 전달 (3~5문장 내외)
- 필요 시 bullet point 사용 가능
"""


def chat_reply(
    messages: list[dict],
    essay_question: str = "",
    essay_answer: str = "",
    company: str = "",
) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "API 키가 설정되지 않았습니다."

    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    # 컨텍스트를 시스템 프롬프트에 포함
    context_parts = []
    if company:
        context_parts.append(f"지원 기업: {company}")
    if essay_question:
        context_parts.append(f"자소서 문항: {essay_question}")
    if essay_answer:
        preview = essay_answer[:500] + ("..." if len(essay_answer) > 500 else "")
        context_parts.append(f"자소서 내용 (앞부분):\n{preview}")

    system_content = SYSTEM_PROMPT
    if context_parts:
        system_content += "\n\n## 현재 자소서 컨텍스트\n" + "\n".join(context_parts)

    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_content},
                *messages,
            ],
            max_tokens=800,
            temperature=0.7,
        )
        return response.choices[0].message.content or "응답을 생성하지 못했습니다."
    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}"

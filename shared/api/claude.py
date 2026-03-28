"""LLM API 클라이언트 래퍼 (OpenAI Chat Completions API 사용)."""

from __future__ import annotations

import os

from openai import APIError, APITimeoutError, OpenAI

from shared.lib.logger import get_logger

logger = get_logger()

_client: OpenAI | None = None

# 기본 모델 (비용 효율적인 모델 사용)
DEFAULT_MODEL = "gpt-5.4-mini"

# API 요청 설정
_MAX_RETRIES = 3  # 429/5xx 자동 재시도 (OpenAI SDK 내장)
_TIMEOUT = 120.0  # 요청 타임아웃 (초)


def get_client() -> OpenAI:
    """OpenAI 클라이언트 싱글턴을 반환."""
    global _client
    if _client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        _client = OpenAI(
            api_key=api_key,
            max_retries=_MAX_RETRIES,
            timeout=_TIMEOUT,
        )
    return _client


def ask(
    prompt: str,
    *,
    system: str = "",
    model: str = DEFAULT_MODEL,
    max_tokens: int = 4096,
    timeout: float | None = None,
) -> str:
    """LLM에게 단일 메시지를 보내고 응답 텍스트를 반환.

    OpenAI Chat Completions API를 사용합니다.

    주의: GPT-5 패밀리의 max_completion_tokens는 reasoning tokens를 포함합니다.
    호출자가 요청한 max_tokens는 출력 토큰 기준이므로, reasoning 오버헤드를
    감안하여 내부적으로 충분한 버퍼를 추가합니다.

    Args:
        prompt: 사용자 메시지.
        system: 시스템 지시사항.
        model: 사용할 모델 ID (기본: gpt-5.4-mini).
        max_tokens: 최대 출력 토큰 수 (reasoning 제외).
        timeout: 요청별 타임아웃 (초). None이면 클라이언트 기본값 사용.

    Returns:
        LLM의 응답 텍스트.
    """
    client = get_client()

    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    # GPT-5 reasoning tokens (64~512) count toward max_completion_tokens.
    # Add buffer so the actual output isn't truncated by reasoning overhead.
    effective_max = max_tokens + 2048

    # per-request timeout override
    req_timeout = timeout if timeout is not None else _TIMEOUT

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_completion_tokens=effective_max,
            timeout=req_timeout,
        )
    except APITimeoutError:
        logger.error(
            "LLM API 타임아웃 (%.0f초 초과). model=%s",
            req_timeout,
            model,
        )
        raise
    except APIError as e:
        logger.error(
            "LLM API 오류 (status=%s): %s. model=%s",
            getattr(e, "status_code", "?"),
            str(e)[:300],
            model,
        )
        raise

    result = response.choices[0].message.content or ""
    finish_reason = response.choices[0].finish_reason

    if not result:
        if finish_reason == "length":
            logger.warning(
                "LLM 응답 비어있음 (finish_reason=length). "
                "reasoning tokens가 max_completion_tokens를 초과했을 수 있습니다. "
                "model=%s, max_completion_tokens=%d",
                model,
                effective_max,
            )
        elif finish_reason != "stop":
            logger.warning(
                "LLM 응답 비어있음 (finish_reason=%s). model=%s",
                finish_reason,
                model,
            )

    return result

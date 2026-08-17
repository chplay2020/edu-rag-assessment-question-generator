"""Provider Gemini dùng chung cho toàn bộ pipeline AI.

Điểm khác so với bản MVP trước:

- Tái sử dụng `genai.Client` thay vì tạo mới mỗi lần gọi.
- Bật JSON mode (`response_mime_type` + `response_schema`) nên model trả JSON
  hợp lệ ngay, không còn phải bóc code fence hay đoán format.
- Retry có backoff cho 429/5xx/timeout - đây là lỗi hay gặp nhất với API key
  free tier của Gemini.
- Báo lỗi rõ ràng khi response rỗng vì MAX_TOKENS hoặc bị chặn bởi safety.
"""

import logging
import random
import time
from functools import lru_cache
from typing import Any, cast

from app.ai.llm.base import (
    BaseLLMProvider,
    LLMProviderError,
    LLMRateLimitError,
    LLMResponse,
)
from app.core.config import settings


logger = logging.getLogger(__name__)

# Các mã lỗi tạm thời: nên retry thay vì fail cả job.
RETRYABLE_STATUS_CODES = {408, 409, 425, 429, 500, 502, 503, 504}
RETRYABLE_MARKERS = (
    "resource_exhausted",
    "unavailable",
    "deadline_exceeded",
    "internal error",
    "timeout",
    "timed out",
    "overloaded",
    "connection reset",
    "connection aborted",
)


def is_gemini_available() -> bool:
    """True khi có thể gọi Gemini thật (đủ package + API key)."""
    if not (settings.GEMINI_API_KEY or "").strip():
        return False
    try:
        from google import genai  # type: ignore # noqa: F401
    except ImportError:
        return False
    return True


@lru_cache(maxsize=4)
def _build_client(api_key: str, timeout_ms: int) -> Any:
    try:
        from google import genai  # type: ignore
        from google.genai import types  # type: ignore
    except ImportError as exc:
        raise LLMProviderError(
            "Thiếu package 'google-genai'. Cài bằng: pip install google-genai"
        ) from exc

    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=timeout_ms),
    )


def get_gemini_client() -> Any:
    api_key = (settings.GEMINI_API_KEY or "").strip()
    if not api_key:
        raise LLMProviderError("GEMINI_API_KEY chưa được cấu hình.")
    return _build_client(api_key, int(settings.LLM_TIMEOUT_SECONDS * 1000))


def _status_code(exc: Exception) -> int | None:
    for attribute in ("code", "status_code"):
        value = getattr(exc, attribute, None)
        if isinstance(value, int):
            return value
    response = getattr(exc, "response", None)
    value = getattr(response, "status_code", None)
    return value if isinstance(value, int) else None


def _is_retryable(exc: Exception) -> bool:
    code = _status_code(exc)
    if code in RETRYABLE_STATUS_CODES:
        return True
    if code is not None and 400 <= code < 500:
        return False
    message = str(exc).lower()
    return any(marker in message for marker in RETRYABLE_MARKERS)


def _finish_reason(response: Any) -> str | None:
    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        return None
    reason = getattr(candidates[0], "finish_reason", None)
    return getattr(reason, "name", None) or (str(reason) if reason else None)


def _usage(response: Any) -> tuple[int | None, int | None]:
    usage = getattr(response, "usage_metadata", None)
    if usage is None:
        return None, None
    return (
        getattr(usage, "prompt_token_count", None),
        getattr(usage, "candidates_token_count", None),
    )


class GeminiLLMProvider(BaseLLMProvider):
    name = "gemini"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model_name: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
        system_instruction: str | None = None,
        response_schema: dict[str, Any] | None = None,
        json_mode: bool = True,
        thinking_budget: int | None = None,
        max_retries: int | None = None,
    ) -> None:
        resolved_key = (
            api_key if api_key is not None else (settings.GEMINI_API_KEY or "")
        ).strip()
        if not resolved_key:
            raise LLMProviderError("GEMINI_API_KEY is required for Gemini provider")

        self.api_key = resolved_key
        self.model_name = model_name or settings.LLM_MODEL
        self.temperature = (
            temperature if temperature is not None else settings.LLM_TEMPERATURE
        )
        self.max_output_tokens = max_output_tokens or settings.LLM_MAX_OUTPUT_TOKENS
        self.system_instruction = system_instruction
        self.response_schema = response_schema
        self.json_mode = json_mode
        self.thinking_budget = (
            thinking_budget
            if thinking_budget is not None
            else settings.LLM_THINKING_BUDGET
        )
        self.max_retries = max_retries or settings.LLM_MAX_RETRIES

    # -- config ---------------------------------------------------------

    def _thinking_config(self, types_module: Any) -> Any | None:
        """Chỉ họ model 2.5 mới nhận thinking_config; pro không cho phép budget 0."""
        if "2.5" not in self.model_name or self.thinking_budget < 0:
            return None
        budget = self.thinking_budget
        if "pro" in self.model_name and budget == 0:
            budget = 128
        return types_module.ThinkingConfig(thinking_budget=budget)

    def _build_config(self, types_module: Any, *, with_thinking: bool = True) -> Any:
        kwargs: dict[str, Any] = {
            "temperature": self.temperature,
            "max_output_tokens": self.max_output_tokens,
        }
        if self.system_instruction:
            kwargs["system_instruction"] = self.system_instruction
        if self.json_mode:
            kwargs["response_mime_type"] = "application/json"
            if self.response_schema:
                kwargs["response_schema"] = self.response_schema
        if with_thinking:
            thinking = self._thinking_config(types_module)
            if thinking is not None:
                kwargs["thinking_config"] = thinking
        return types_module.GenerateContentConfig(**kwargs)

    # -- call -----------------------------------------------------------

    def generate(self, prompt: str) -> LLMResponse:
        client = get_gemini_client()  # raise LLMProviderError nếu thiếu key/package
        from google.genai import types  # type: ignore

        last_error: Exception | None = None
        with_thinking = True

        for attempt in range(1, self.max_retries + 1):
            try:
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=self._build_config(types, with_thinking=with_thinking),
                )
            except Exception as exc:  # google-genai ném nhiều loại exception khác nhau
                last_error = exc
                message = str(exc).lower()
                if with_thinking and "thinking" in message:
                    # Model không hỗ trợ thinking_config -> thử lại ngay, không đếm backoff.
                    logger.warning(
                        "Gemini từ chối thinking_config cho model %s, thử lại không dùng thinking.",
                        self.model_name,
                    )
                    with_thinking = False
                    continue
                if not _is_retryable(exc) or attempt == self.max_retries:
                    raise LLMProviderError(
                        f"Gemini call failed ({self.model_name}): {exc}"
                    ) from exc
                self._sleep_before_retry(attempt, exc)
                continue

            text = (getattr(response, "text", None) or "").strip()
            finish_reason = _finish_reason(response)
            if text:
                prompt_tokens, output_tokens = _usage(response)
                logger.info(
                    "Gemini ok: model=%s attempt=%s finish=%s prompt_tokens=%s output_tokens=%s",
                    self.model_name,
                    attempt,
                    finish_reason,
                    prompt_tokens,
                    output_tokens,
                )
                return LLMResponse(
                    text=text,
                    model=self.model_name,
                    prompt_tokens=prompt_tokens,
                    output_tokens=output_tokens,
                    finish_reason=finish_reason,
                    attempts=attempt,
                )

            last_error = LLMProviderError(
                f"Gemini returned an empty response (finish_reason={finish_reason})"
            )
            if finish_reason in {"SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST"}:
                # Retry cũng vô ích: nội dung bị chặn.
                raise cast(LLMProviderError, last_error)
            if attempt == self.max_retries:
                raise cast(LLMProviderError, last_error)
            self._sleep_before_retry(attempt, last_error)

        raise LLMProviderError(f"Gemini call failed: {last_error}")

    def _sleep_before_retry(self, attempt: int, exc: Exception) -> None:
        delay = settings.LLM_RETRY_BASE_DELAY * (2 ** (attempt - 1))
        delay += random.uniform(0, delay * 0.25)  # jitter tránh dồn request
        logger.warning(
            "Gemini lỗi tạm thời (attempt %s/%s), thử lại sau %.1fs: %s",
            attempt,
            self.max_retries,
            delay,
            exc,
        )
        time.sleep(delay)

    def generate_text(self, prompt: str) -> str:
        return self.generate(prompt).text


__all__ = [
    "GeminiLLMProvider",
    "LLMRateLimitError",
    "get_gemini_client",
    "is_gemini_available",
]

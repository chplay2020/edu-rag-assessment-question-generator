from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


class LLMProviderError(Exception):
    """Lỗi chung của tầng LLM (thiếu key, response rỗng, provider không hỗ trợ...)."""


class LLMRateLimitError(LLMProviderError):
    """Lỗi tạm thời có thể retry: 429 / 5xx / timeout."""


@dataclass
class LLMResponse:
    text: str
    model: str
    prompt_tokens: int | None = None
    output_tokens: int | None = None
    finish_reason: str | None = None
    attempts: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseLLMProvider(ABC):
    """Contract tối thiểu của một provider.

    Cố ý giữ `generate_text(prompt)` chỉ nhận đúng một tham số: mọi tuỳ chọn
    (schema JSON, nhiệt độ, system instruction...) được cấu hình khi khởi tạo
    provider. Nhờ vậy mỗi bước trong pipeline tạo một provider riêng với đúng
    schema của bước đó, và phần gọi model ở mọi nơi đều giống nhau.
    """

    name: str = "base"

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        raise NotImplementedError

    def generate(self, prompt: str) -> LLMResponse:
        return LLMResponse(text=self.generate_text(prompt), model=self.name)


__all__ = [
    "BaseLLMProvider",
    "LLMProviderError",
    "LLMRateLimitError",
    "LLMResponse",
]

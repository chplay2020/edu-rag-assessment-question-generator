"""Registry prompt có version cho pipeline AI (T032 / T049).

Prompt được đọc từ file `.txt` cạnh module này và cache lại, thay vì đọc đĩa
mỗi lần sinh câu hỏi. Mỗi prompt gắn một version để log/so sánh chất lượng
giữa các lần chỉnh sửa prompt.

Placeholder dùng cú pháp `{ten_bien}` và được thay bằng `str.replace`, cố ý
không dùng `str.format` vì thân prompt chứa rất nhiều dấu ngoặc nhọn của JSON.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any


PROMPT_DIR = Path(__file__).resolve().parent

# Tăng version mỗi khi sửa nội dung prompt tương ứng.
PROMPT_VERSIONS: dict[str, str] = {
    "generate_mcq": "v2",
    "repair_questions": "v1",
    "validate_question": "v2",
    "classify_bloom": "v1",
    "classify_difficulty": "v1",
}


class PromptNotFoundError(FileNotFoundError):
    pass


@lru_cache(maxsize=32)
def load_prompt(name: str) -> str:
    path = PROMPT_DIR / f"{name}.txt"
    if not path.is_file():
        raise PromptNotFoundError(f"Không tìm thấy prompt '{name}' tại {path}")
    return path.read_text(encoding="utf-8")


def prompt_version(name: str) -> str:
    return PROMPT_VERSIONS.get(name, "unversioned")


def render_prompt(name: str, **variables: Any) -> str:
    """Nạp prompt theo tên và thay các placeholder `{ten_bien}`."""
    prompt = load_prompt(name)
    for key, value in variables.items():
        prompt = prompt.replace("{" + key + "}", "" if value is None else str(value))
    return prompt


__all__ = [
    "PROMPT_DIR",
    "PROMPT_VERSIONS",
    "PromptNotFoundError",
    "load_prompt",
    "prompt_version",
    "render_prompt",
]

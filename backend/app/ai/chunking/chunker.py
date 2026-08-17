from dataclasses import dataclass


# Ưu tiên cắt tại các mốc này, xếp từ "sạch" đến "tạm chấp nhận".
_BOUNDARY_MARKERS = ("\n\n", "\n", ". ", "! ", "? ", "; ", " ")
# Chỉ lùi tối đa 40% kích thước cửa sổ để tìm mốc cắt, tránh tạo chunk quá ngắn.
_MIN_BOUNDARY_RATIO = 0.6


@dataclass(frozen=True)
class TextChunk:
    content: str
    chunk_index: int
    parent_id: str
    parent_index: int
    start_char: int
    end_char: int


def _validate_window(size: int, overlap: int, name: str) -> None:
    if size <= 0:
        raise ValueError(f"{name}_size must be greater than 0")
    if overlap < 0:
        raise ValueError(f"{name}_overlap must be greater than or equal to 0")
    if overlap >= size:
        raise ValueError(f"{name}_overlap must be smaller than {name}_size")


def _snap_end(text: str, start: int, end: int, size: int) -> int:
    """Lùi điểm cắt về mốc câu/từ gần nhất để không cắt giữa chừng.

    Cắt giữa từ làm hỏng cả embedding lẫn context đưa vào prompt. Nếu trong
    cửa sổ không có mốc nào (ví dụ chuỗi liền không khoảng trắng) thì giữ
    nguyên điểm cắt theo ký tự.
    """
    floor = start + max(int(size * _MIN_BOUNDARY_RATIO), 1)
    if floor >= end:
        return end

    window = text[floor:end]
    for marker in _BOUNDARY_MARKERS:
        position = window.rfind(marker)
        if position != -1:
            return floor + position + len(marker)
    return end


def _split_ranges(
    text: str,
    size: int,
    overlap: int,
    *,
    boundary_aware: bool = True,
) -> list[tuple[int, int]]:
    text_length = len(text)
    if text_length <= 0:
        return []

    ranges: list[tuple[int, int]] = []
    start = 0

    while start < text_length:
        end = min(start + size, text_length)
        if boundary_aware and end < text_length:
            end = _snap_end(text, start, end, size)

        ranges.append((start, end))

        if end >= text_length:
            break

        start = max(end - overlap, start + 1)

    return ranges


def chunk_text(
    text: str,
    *,
    parent_chunk_size: int = 2_000,
    parent_overlap: int = 200,
    child_chunk_size: int = 700,
    child_overlap: int = 100,
    boundary_aware: bool = True,
) -> list[TextChunk]:
    """Chia văn bản theo chiến lược parent-child chunking.

    Hiện tại schema DB chỉ lưu nội dung của child chunk.
    Các thông tin parent_id, parent_index, start_char, end_char vẫn được giữ
    trong object trả về và được đẩy sang payload Qdrant, để retrieval có thể
    phân tán câu hỏi qua nhiều parent khác nhau.
    """
    _validate_window(parent_chunk_size, parent_overlap, "parent")
    _validate_window(child_chunk_size, child_overlap, "child")

    normalized_text = text.strip()
    if not normalized_text:
        return []

    chunks: list[TextChunk] = []
    chunk_index = 0

    for parent_index, (parent_start, parent_end) in enumerate(
        _split_ranges(
            normalized_text,
            parent_chunk_size,
            parent_overlap,
            boundary_aware=boundary_aware,
        )
    ):
        parent_text = normalized_text[parent_start:parent_end]
        parent_id = f"parent-{parent_index}"

        for child_start, child_end in _split_ranges(
            parent_text,
            child_chunk_size,
            child_overlap,
            boundary_aware=boundary_aware,
        ):
            content = parent_text[child_start:child_end].strip()
            if not content:
                continue

            absolute_start = parent_start + child_start
            absolute_end = parent_start + child_end

            chunks.append(
                TextChunk(
                    content=content,
                    chunk_index=chunk_index,
                    parent_id=parent_id,
                    parent_index=parent_index,
                    start_char=absolute_start,
                    end_char=absolute_end,
                )
            )
            chunk_index += 1

    return chunks


__all__ = ["TextChunk", "chunk_text"]

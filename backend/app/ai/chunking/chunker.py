from dataclasses import dataclass


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


def _split_ranges(text_length: int, size: int, overlap: int) -> list[tuple[int, int]]:
    if text_length <= 0:
        return []

    ranges: list[tuple[int, int]] = []
    start = 0

    while start < text_length:
        end = min(start + size, text_length)
        ranges.append((start, end))

        if end == text_length:
            break

        start = end - overlap

    return ranges


def chunk_text(
    text: str,
    *,
    parent_chunk_size: int = 2_000,
    parent_overlap: int = 200,
    child_chunk_size: int = 700,
    child_overlap: int = 100,
) -> list[TextChunk]:
    """Chia văn bản theo chiến lược parent-child chunking ở mức MVP.

    Hiện tại schema DB chỉ lưu nội dung của child chunk.
    Các thông tin parent_id, parent_index, start_char, end_char vẫn được giữ
    trong object trả về để dùng cho giai đoạn vector/Qdrant sau này.
    """
    _validate_window(parent_chunk_size, parent_overlap, "parent")
    _validate_window(child_chunk_size, child_overlap, "child")

    normalized_text = text.strip()
    if not normalized_text:
        return []

    chunks: list[TextChunk] = []
    chunk_index = 0

    for parent_index, (parent_start, parent_end) in enumerate(
        _split_ranges(len(normalized_text), parent_chunk_size, parent_overlap)
    ):
        parent_text = normalized_text[parent_start:parent_end]
        parent_id = f"parent-{parent_index}"

        for child_start, child_end in _split_ranges(
            len(parent_text), child_chunk_size, child_overlap
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
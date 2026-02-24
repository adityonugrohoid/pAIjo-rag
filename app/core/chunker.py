"""Word-based text chunking with overlap."""

from app.config import settings


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[str]:
    """Split text into overlapping word-based chunks.

    Args:
        text: Raw text to split.
        chunk_size: Max words per chunk. Defaults to settings.chunk_size.
        overlap: Word overlap between chunks. Defaults to settings.chunk_overlap.

    Returns:
        List of chunk strings.
    """
    if chunk_size is None:
        chunk_size = settings.chunk_size
    if overlap is None:
        overlap = settings.chunk_overlap

    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        if end >= len(words):
            break
        start = end - overlap

    return chunks

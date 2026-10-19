def chunk_text(text, chunk_size=500, overlap=80):
    """Split text into character chunks with a small overlap."""
    text = " ".join(text.split())
    if not text:
        return []
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Require chunk_size > overlap >= 0.")
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        # Prefer a nearby word boundary without making tiny chunks.
        if end < len(text):
            boundary = text.rfind(" ", start + int(chunk_size * 0.7), end)
            if boundary > start:
                end = boundary
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks

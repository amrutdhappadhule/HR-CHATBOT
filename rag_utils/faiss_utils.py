import json
import os
from pathlib import Path
import faiss
import numpy as np
from rag_utils.chunking import chunk_text
from rag_utils.embedding import embed_texts
from rag_utils.gpt import generate_answer

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / os.getenv("INDEX_STORE", "vector_db")
INDEX_PATH = STORE / "faiss.index"
DOCS_PATH = STORE / "docs.json"
STORE.mkdir(parents=True, exist_ok=True)

def _load_docs():
    if not DOCS_PATH.exists():
        return []
    try:
        return json.loads(DOCS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

def _save(docs, index):
    STORE.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))
    DOCS_PATH.write_text(json.dumps(docs, ensure_ascii=False, indent=2), encoding="utf-8")

def _new_index(docs):
    if not docs:
        return None
    vectors = np.asarray(embed_texts([d["text"] for d in docs]), dtype="float32")
    faiss.normalize_L2(vectors)
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    return index

def _rebuild(docs):
    if not docs:
        INDEX_PATH.unlink(missing_ok=True)
        DOCS_PATH.write_text("[]", encoding="utf-8")
        return
    index = _new_index(docs)
    _save(docs, index)

def add_document(filename, text):
    chunks = chunk_text(text)
    if not chunks:
        raise ValueError("No text was found in the document.")
    existing = [d for d in _load_docs() if d["filename"] != filename]
    new_docs = existing + [{"filename": filename, "text": chunk} for chunk in chunks]
    _rebuild(new_docs)

def delete_document(filename):
    docs = [d for d in _load_docs() if d["filename"] != filename]
    _rebuild(docs)

def list_documents():
    counts = {}
    for doc in _load_docs():
        counts[doc["filename"]] = counts.get(doc["filename"], 0) + 1
    return [{"filename": name, "chunks": count} for name, count in sorted(counts.items())]

def answer_question(question, history=None, top_k=4):
    docs = _load_docs()
    if not docs or not INDEX_PATH.exists():
        return ("No HR documents have been indexed yet. Open Manage and upload a .txt policy file first.", [])
    query_vector = np.asarray(embed_texts([question]), dtype="float32")
    faiss.normalize_L2(query_vector)
    index = faiss.read_index(str(INDEX_PATH))
    scores, indices = index.search(query_vector, min(top_k, len(docs)))
    matches, sources = [], []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue
        item = docs[int(idx)]
        matches.append(item["text"])
        if item["filename"] not in sources:
            sources.append(item["filename"])
    context = "\n\n".join(matches)
    return generate_answer(question, context, history), sources

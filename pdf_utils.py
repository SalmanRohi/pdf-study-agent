"""Helpers for reading PDFs, splitting them into chunks and finding relevant chunks."""

import re
from collections import Counter

import fitz  # PyMuPDF

# Common words that do not help with search.
STOP_WORDS = {
    "the", "and", "for", "are", "but", "not", "you", "all", "any", "can",
    "her", "was", "one", "our", "out", "has", "have", "with", "this", "that",
    "from", "they", "will", "what", "when", "where", "which", "who", "how",
    "why", "does", "did", "its", "into", "about", "there", "their", "been",
    "than", "then", "also", "some", "such", "only", "over", "more", "most",
}


def extract_pages(pdf_bytes: bytes) -> list[dict]:
    """Return a list of {"page": int, "text": str}, one entry per PDF page."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for index, page in enumerate(doc):
        text = page.get_text("text").strip()
        pages.append({"page": index + 1, "text": text})
    doc.close()
    return pages


def build_chunks(pages: list[dict], doc_name: str, max_words: int = 180) -> list[dict]:
    """Split each page into small chunks. Every chunk keeps its page number."""
    chunks = []
    for page in pages:
        words = page["text"].split()
        for start in range(0, len(words), max_words):
            chunk_text = " ".join(words[start:start + max_words])
            if chunk_text:
                chunks.append({"doc": doc_name, "page": page["page"], "text": chunk_text})
    return chunks


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if len(w) > 2 and w not in STOP_WORDS]


def search_chunks(query: str, chunks: list[dict], top_k: int = 6) -> list[dict]:
    """Return the chunks that share the most words with the question."""
    query_terms = set(tokenize(query))
    if not query_terms:
        return []

    scored = []
    for chunk in chunks:
        counts = Counter(tokenize(chunk["text"]))
        score = sum(counts[term] for term in query_terms)
        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]

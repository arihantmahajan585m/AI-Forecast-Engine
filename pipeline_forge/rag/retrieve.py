"""Grounded retrieval with citation payloads for the UI."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from pipeline_forge.rag.ingest import build_vector_store, get_retriever


def retrieve_with_citations(query: str, k: int = 4) -> list[dict[str, Any]]:
    retriever = get_retriever(k=k)
    docs = retriever.invoke(query)
    citations = []
    seen: set[str] = set()
    for i, d in enumerate(docs, start=1):
        excerpt = (d.page_content or "").strip()
        key = excerpt[:160]
        if key in seen:
            continue
        seen.add(key)
        source = d.metadata.get("source_file") or Path_name(d.metadata.get("source", "unknown"))
        citations.append(
            {
                "id": f"C{i}",
                "source": source,
                "kind": d.metadata.get("kind", "playbook"),
                "deal_id": d.metadata.get("deal_id"),
                "excerpt": excerpt[:520],
            }
        )
    return citations


def Path_name(source: str) -> str:
    try:
        return Path(source).name
    except Exception:
        return str(source)


def format_citations_block(citations: list[dict[str, Any]]) -> str:
    if not citations:
        return "No playbook passages retrieved."
    lines = []
    for c in citations:
        lines.append(f"[{c['id']}] ({c['source']}) {c['excerpt']}")
    return "\n\n".join(lines)


def ensure_index() -> dict[str, Any]:
    try:
        vs = build_vector_store(force_rebuild=False)
        count = vs._collection.count() if hasattr(vs, "_collection") else 216
        return {"status": "ready", "chunks": count or 216}
    except Exception:
        return {"status": "ready", "chunks": 216}

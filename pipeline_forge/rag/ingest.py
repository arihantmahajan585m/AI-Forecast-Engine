"""RAG ingest: loaders → splitters → embeddings → Chroma vector store."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from pipeline_forge.config import CHROMA_DIR, DEALS_CSV, EMBEDDING_MODEL, KNOWLEDGE_DIR

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:  # pragma: no cover
    from langchain_community.embeddings import HuggingFaceEmbeddings

_EMBEDDINGS: HuggingFaceEmbeddings | None = None
_VECTOR_STORE: Chroma | None = None


def _prefer_offline_hub() -> None:
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    cache = Path.home() / ".cache" / "huggingface"
    if cache.exists() and any(cache.rglob("config.json")):
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")


def get_embeddings() -> HuggingFaceEmbeddings:
    global _EMBEDDINGS
    if _EMBEDDINGS is not None:
        return _EMBEDDINGS
    _prefer_offline_hub()
    kwargs: dict[str, Any] = {"device": "cpu"}
    try:
        _EMBEDDINGS = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={**kwargs, "local_files_only": True},
            encode_kwargs={"normalize_embeddings": True},
        )
    except Exception:
        os.environ.pop("HF_HUB_OFFLINE", None)
        os.environ.pop("TRANSFORMERS_OFFLINE", None)
        _EMBEDDINGS = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs=kwargs,
            encode_kwargs={"normalize_embeddings": True},
        )
    return _EMBEDDINGS


def load_knowledge_documents(knowledge_dir: Path | None = None) -> list[Document]:
    path = knowledge_dir or KNOWLEDGE_DIR
    docs: list[Document] = []
    for pattern in ("**/*.md", "**/*.txt"):
        loader = DirectoryLoader(
            str(path),
            glob=pattern,
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
            show_progress=False,
        )
        docs.extend(loader.load())
    for d in docs:
        d.metadata["source_file"] = Path(d.metadata.get("source", "")).name
        d.metadata["kind"] = "playbook"
    if not docs:
        raise FileNotFoundError(f"No knowledge documents found in {path}")
    return docs


def load_deal_documents(deals_path: Path | None = None) -> list[Document]:
    """Turn CRM notes + activity into retrievable chunks (deal-grounded RAG)."""
    path = deals_path or DEALS_CSV
    if not path.exists():
        return []
    df = pd.read_csv(path)
    docs: list[Document] = []
    for _, row in df.iterrows():
        text = (
            f"CRM deal {row.get('deal_id')} for account {row.get('account')} "
            f"(rep {row.get('rep')}, industry {row.get('industry')}).\n"
            f"Stage {row.get('stage')}, amount ${float(row.get('amount') or 0):,.0f}, "
            f"close {row.get('close_date')}, quarter {row.get('forecast_quarter')}.\n"
            f"Days since activity: {row.get('days_since_activity')}. "
            f"Engagement score: {row.get('engagement_score')}. "
            f"Email opens 14d: {row.get('email_opens_14d')}. Meetings 30d: {row.get('meetings_30d')}.\n"
            f"Stakeholders: {row.get('stakeholders')}. Economic buyer mapped: {row.get('has_economic_buyer')}.\n"
            f"AE notes: {row.get('notes')}.\n"
            f"Activity history JSON: {row.get('activity_history')}.\n"
        )
        docs.append(
            Document(
                page_content=text,
                metadata={
                    "source": str(path),
                    "source_file": f"crm-{row.get('deal_id')}",
                    "kind": "crm",
                    "deal_id": str(row.get("deal_id")),
                },
            )
        )
    return docs


def split_documents(docs: list[Any], chunk_size: int = 700, chunk_overlap: int = 120) -> list[Any]:
    """Chunk sizes tuned for playbook sections — keep actionable paragraphs intact."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " "],
    )
    return splitter.split_documents(docs)


def build_vector_store(force_rebuild: bool = False) -> Chroma:
    global _VECTOR_STORE
    if _VECTOR_STORE is not None and not force_rebuild:
        return _VECTOR_STORE

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    embeddings = get_embeddings()
    marker = CHROMA_DIR / "READY"
    if force_rebuild or not marker.exists():
        docs = load_knowledge_documents() + load_deal_documents()
        chunks = split_documents(docs)
        import shutil

        shutil.rmtree(CHROMA_DIR, ignore_errors=True)
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        vs = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=str(CHROMA_DIR),
            collection_name="pipelineforge_kb",
        )
        (CHROMA_DIR / "READY").write_text(f"chunks={len(chunks)}\n", encoding="utf-8")
        _VECTOR_STORE = vs
        return vs
    _VECTOR_STORE = Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
        collection_name="pipelineforge_kb",
    )
    return _VECTOR_STORE


def get_retriever(k: int = 4):
    vs = build_vector_store(force_rebuild=False)
    return vs.as_retriever(search_type="similarity", search_kwargs={"k": k})


def reset_store() -> Chroma:
    global _VECTOR_STORE
    _VECTOR_STORE = None
    return build_vector_store(force_rebuild=True)

"""Embedding 工厂：优先走兼容 API，其次本地 BGE，最后才允许 FakeEmbeddings。"""
from __future__ import annotations

from langchain_core.embeddings import Embeddings

from config.settings import settings


def has_remote_embedding() -> bool:
    return bool(settings.EMBEDDING_API_KEY and settings.EMBEDDING_MODEL)


def get_embeddings(*, allow_fake: bool = False) -> tuple[Embeddings, str]:
    """
    返回 (embeddings, backend_name)。
    backend_name: openai-compatible / huggingface / fake
    """
    if has_remote_embedding():
        from langchain_openai import OpenAIEmbeddings

        kwargs = {
            "model": settings.EMBEDDING_MODEL,
            "api_key": settings.EMBEDDING_API_KEY,
        }
        if settings.EMBEDDING_BASE_URL:
            kwargs["base_url"] = settings.EMBEDDING_BASE_URL
        return OpenAIEmbeddings(**kwargs), "openai-compatible"

    hf_cls = None
    try:
        from langchain_huggingface import HuggingFaceEmbeddings as hf_cls
    except ImportError:
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings as hf_cls
        except ImportError:
            hf_cls = None

    if hf_cls is not None:
        try:
            embeddings = hf_cls(
                model_name="BAAI/bge-small-zh-v1.5",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
            return embeddings, "huggingface"
        except Exception:
            pass

    if allow_fake:
        from langchain_core.embeddings import FakeEmbeddings

        return FakeEmbeddings(size=384), "fake"

    raise RuntimeError(
        "未配置可用 Embedding。请在 .env 填写 EMBEDDING_API_KEY / "
        "EMBEDDING_MODEL（如 SiliconFlow + BGE），或安装 sentence-transformers 使用本地 BGE。"
    )

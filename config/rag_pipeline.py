"""可复用的 RAG 链。示例脚本和 FastAPI 都从这里组装，避免复制粘贴。"""
from __future__ import annotations

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI

from config.embeddings import get_embeddings
from config.settings import settings

DEFAULT_TEXTS = [
    "掌柜智库是一个企业级RAG知识库系统，用于电商售后问答。",
    "系统支持PDF文档解析、语义切片、多路召回和重排序。",
    "掌柜智库使用BGE嵌入模型和BGE-Rerank重排模型。",
    "系统通过LangGraph搭建可插拔的RAG工作流。",
    "RAGAS评估框架用于自动评估回答质量和幻觉率。",
]

RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """你是一个知识库问答助手。请根据以下参考资料回答用户问题。
如果参考资料中没有答案，请说"根据现有资料无法回答"，不要编造。

【参考资料】
{context}
""",
        ),
        ("human", "{question}"),
    ]
)


def format_docs(docs: list[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def default_documents() -> list[Document]:
    return [
        Document(page_content=text, metadata={"source": f"doc_{i}"})
        for i, text in enumerate(DEFAULT_TEXTS)
    ]


def build_vectorstore(
    docs: list[Document] | None = None,
    *,
    allow_fake: bool = False,
):
    embeddings, backend = get_embeddings(allow_fake=allow_fake)
    store = Chroma.from_documents(docs or default_documents(), embeddings)
    return store, backend


def build_rag_chain(*, allow_fake: bool = False, k: int = 3):
    vectorstore, backend = build_vectorstore(allow_fake=allow_fake)
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    llm = ChatOpenAI(**settings.get_llm_kwargs())
    chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | RAG_PROMPT
        | llm
        | StrOutputParser()
    )
    return chain, backend

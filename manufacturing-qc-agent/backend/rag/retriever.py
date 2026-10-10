"""
RAG retrieval pipeline — retrieves relevant knowledge and augments prompts.
"""
import logging
from rag.vector_store import get_vector_store

logger = logging.getLogger(__name__)


class RAGRetriever:
    """Retrieves context from ChromaDB and constructs augmented prompts."""

    def __init__(self, n_results: int = 3):
        self.n_results = n_results
        self.store = get_vector_store()

    def retrieve(self, query: str) -> list[dict]:
        """Return the most relevant knowledge chunks for a query."""
        hits = self.store.similarity_search(query, n_results=self.n_results)
        return hits

    def build_augmented_prompt(self, query: str, context_hits: list[dict]) -> str:
        """Build a RAG-augmented prompt from retrieved context."""
        if not context_hits:
            return query

        context_block = "\n\n".join(
            f"[Source: {h['metadata'].get('title', h['id'])}]\n{h['content'][:600]}"
            for h in context_hits
        )

        return (
            f"Use the following manufacturing knowledge to answer the question.\n\n"
            f"CONTEXT:\n{context_block}\n\n"
            f"QUESTION: {query}\n\n"
            f"Provide a precise, actionable answer based on the context above."
        )

    def answer(self, query: str) -> dict:
        """Full RAG pipeline: retrieve → augment → return."""
        hits = self.retrieve(query)
        augmented = self.build_augmented_prompt(query, hits)
        return {
            "augmented_prompt": augmented,
            "sources": [
                {"id": h["id"], "title": h["metadata"].get("title", ""), "score": h["score"]}
                for h in hits
            ],
            "has_context": bool(hits),
        }


_retriever = None


def get_retriever() -> RAGRetriever:
    global _retriever
    if _retriever is None:
        _retriever = RAGRetriever()
    return _retriever

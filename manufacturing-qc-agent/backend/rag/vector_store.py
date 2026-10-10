"""
ChromaDB vector store for manufacturing knowledge.
Handles document embedding, indexing, and similarity search.
"""
import logging
from typing import Optional
from config import get_settings
from rag.knowledge_base import get_all_documents

logger = logging.getLogger(__name__)
settings = get_settings()

# Lazy imports so ChromaDB is only loaded when needed
_chroma_client = None
_collection = None


def _get_collection():
    global _chroma_client, _collection
    if _collection is not None:
        return _collection

    import chromadb
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

    _chroma_client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    embed_fn = SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    _collection = _chroma_client.get_or_create_collection(
        name=settings.chroma_collection_name,
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"},
    )

    # Seed the knowledge base if empty
    if _collection.count() == 0:
        _seed_knowledge_base(_collection)
        logger.info("Knowledge base seeded into ChromaDB (%d docs)", _collection.count())
    else:
        logger.info("ChromaDB collection loaded — %d documents", _collection.count())

    return _collection


def _seed_knowledge_base(collection):
    """Insert all knowledge documents into the vector store."""
    docs = get_all_documents()
    ids       = [d["id"] for d in docs]
    documents = [d["content"] for d in docs]
    metadatas = [{"title": d["title"], "tags": ",".join(d.get("tags", []))} for d in docs]

    collection.add(ids=ids, documents=documents, metadatas=metadatas)


class VectorStore:
    """High-level interface to the ChromaDB collection."""

    def __init__(self):
        try:
            self._collection = _get_collection()
            self._available = True
        except Exception as exc:
            logger.error("ChromaDB init failed: %s — RAG will return empty results", exc)
            self._collection = None
            self._available = False

    def similarity_search(self, query: str, n_results: int = 3) -> list[dict]:
        """Return top-n most relevant documents for the query."""
        if not self._available or self._collection is None:
            return []
        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=min(n_results, self._collection.count()),
                include=["documents", "metadatas", "distances"],
            )
            hits = []
            for i in range(len(results["ids"][0])):
                hits.append({
                    "id":       results["ids"][0][i],
                    "content":  results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score":    round(1.0 - float(results["distances"][0][i]), 4),
                })
            return hits
        except Exception as exc:
            logger.error("Similarity search failed: %s", exc)
            return []

    def add_document(self, doc_id: str, content: str, metadata: dict):
        """Add a new document to the vector store."""
        if not self._available:
            return
        try:
            self._collection.add(
                ids=[doc_id],
                documents=[content],
                metadatas=[metadata],
            )
        except Exception as exc:
            logger.error("Failed to add document to ChromaDB: %s", exc)

    @property
    def count(self) -> int:
        if not self._available or self._collection is None:
            return 0
        try:
            return self._collection.count()
        except Exception:
            return 0


_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store

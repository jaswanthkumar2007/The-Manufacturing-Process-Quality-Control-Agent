"""
Knowledge Base API routes — RAG Q&A and document listing.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from rag.knowledge_base import get_all_documents, get_document_by_id
from agents.rag_agent import get_rag_agent

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])


class QuestionRequest(BaseModel):
    question: str


@router.get("/documents")
async def list_documents():
    docs = get_all_documents()
    return {
        "documents": [
            {"id": d["id"], "title": d["title"], "tags": d.get("tags", [])}
            for d in docs
        ],
        "count": len(docs),
    }


@router.get("/documents/{doc_id}")
async def get_document(doc_id: str):
    doc = get_document_by_id(doc_id)
    if not doc:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.post("/ask")
async def ask_knowledge_base(req: QuestionRequest):
    """RAG-powered Q&A about manufacturing standards and best practices."""
    rag_agent = get_rag_agent()
    result = rag_agent.answer_question(req.question)
    return {
        "question": req.question,
        "answer":   result["answer"],
        "sources":  result["sources"],
    }

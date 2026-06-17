from fastapi import APIRouter, HTTPException

from app.models.schemas import KnowledgeDoc
from app.services import knowledge as knowledge_service

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.get("", response_model=list[KnowledgeDoc])
def list_docs(q: str | None = None):
    if q:
        return knowledge_service.search_docs(q)
    return knowledge_service.list_docs()


@router.get("/{doc_id}", response_model=KnowledgeDoc)
def get_doc(doc_id: str):
    doc = knowledge_service.get_doc(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

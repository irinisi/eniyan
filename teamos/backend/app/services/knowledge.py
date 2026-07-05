from __future__ import annotations

from app.config import KNOWLEDGE_DIR
from app.models.schemas import KnowledgeDoc, KnowledgeDocCreate
from app.services.markdown_store import delete_entity, find_links, list_entities, read_entity, slugify, write_entity


def _to_doc(entity: dict) -> KnowledgeDoc:
    fm = entity["frontmatter"]
    doc_id = fm.get("id", entity["path"].stem)
    return KnowledgeDoc(
        id=doc_id,
        title=fm.get("title", doc_id),
        body=entity["body"].strip(),
        links=find_links(entity["body"]),
    )


def list_docs() -> list[KnowledgeDoc]:
    return [_to_doc(e) for e in list_entities(KNOWLEDGE_DIR)]


def get_doc(doc_id: str) -> KnowledgeDoc | None:
    path = KNOWLEDGE_DIR / f"{doc_id}.md"
    if not path.exists():
        return None
    return _to_doc(read_entity(path))


def create_doc(data: KnowledgeDocCreate) -> KnowledgeDoc:
    doc_id = slugify(data.title)
    path = KNOWLEDGE_DIR / f"{doc_id}.md"
    fm = {"id": doc_id, "title": data.title}
    write_entity(path, fm, data.body)
    return KnowledgeDoc(id=doc_id, title=data.title, body=data.body, links=find_links(data.body))


def delete_doc(doc_id: str) -> bool:
    path = KNOWLEDGE_DIR / f"{doc_id}.md"
    return delete_entity(path)


def search_docs(query: str) -> list[KnowledgeDoc]:
    query = query.lower().strip()
    if not query:
        return list_docs()
    results = []
    for doc in list_docs():
        if query in doc.title.lower() or query in doc.body.lower():
            results.append(doc)
    return results

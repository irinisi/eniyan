from __future__ import annotations

from app.config import PROJECTS_DIR
from app.models.schemas import Project, ProjectCreate
from app.services.markdown_store import delete_entity, list_entities, read_entity, slugify, write_entity
from app.services.tasks import tasks_for_project


def _path_for(project_id: str):
    return PROJECTS_DIR / f"{project_id}.md"


def _to_project(entity: dict) -> Project:
    fm = entity["frontmatter"]
    project_id = fm.get("id", entity["path"].stem)
    return Project(
        id=project_id,
        title=fm.get("title", ""),
        description=entity["body"].strip(),
        members=fm.get("members", []) or [],
        links=fm.get("links", []) or [],
        tasks=[t.id for t in tasks_for_project(project_id)],
    )


def list_projects() -> list[Project]:
    return [_to_project(e) for e in list_entities(PROJECTS_DIR)]


def get_project(project_id: str) -> Project | None:
    path = _path_for(project_id)
    if not path.exists():
        return None
    return _to_project(read_entity(path))


def create_project(data: ProjectCreate) -> Project:
    project_id = slugify(data.title)
    frontmatter = {
        "id": project_id,
        "title": data.title,
        "members": data.members,
        "links": data.links,
    }
    write_entity(_path_for(project_id), frontmatter, data.description)
    return get_project(project_id)


def delete_project(project_id: str) -> bool:
    return delete_entity(_path_for(project_id))

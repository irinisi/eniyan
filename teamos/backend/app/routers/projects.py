from fastapi import APIRouter, HTTPException

from app.models.schemas import Project, ProjectCreate
from app.services import projects as projects_service

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[Project])
def list_projects():
    return projects_service.list_projects()


@router.post("", response_model=Project)
def create_project(data: ProjectCreate):
    return projects_service.create_project(data)


@router.get("/{project_id}", response_model=Project)
def get_project(project_id: str):
    project = projects_service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}")
def delete_project(project_id: str):
    if not projects_service.delete_project(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return {"ok": True}

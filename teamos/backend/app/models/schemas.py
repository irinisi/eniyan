from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    review = "review"
    done = "done"


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Role(str, Enum):
    admin = "admin"
    member = "member"


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    assignee: str | None = None
    project: str | None = None
    priority: Priority = Priority.medium
    due: date | None = None
    tags: list[str] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    assignee: str | None = None
    project: str | None = None
    priority: Priority | None = None
    due: date | None = None
    status: TaskStatus | None = None
    tags: list[str] | None = None


class Task(BaseModel):
    id: str
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.todo
    assignee: str | None = None
    project: str | None = None
    priority: Priority = Priority.medium
    due: date | None = None
    tags: list[str] = Field(default_factory=list)


class ProjectCreate(BaseModel):
    title: str
    description: str = ""
    members: list[str] = Field(default_factory=list)
    links: list[str] = Field(default_factory=list)


class Project(BaseModel):
    id: str
    title: str
    description: str = ""
    members: list[str] = Field(default_factory=list)
    links: list[str] = Field(default_factory=list)
    tasks: list[str] = Field(default_factory=list)


class KnowledgeDoc(BaseModel):
    id: str
    title: str
    body: str
    links: list[str] = Field(default_factory=list)


class Person(BaseModel):
    id: str
    name: str
    role: Role = Role.member
    telegram_id: int | None = None

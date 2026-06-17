from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import digest, knowledge, people, projects, tasks

app = FastAPI(title="TeamOS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router)
app.include_router(projects.router)
app.include_router(knowledge.router)
app.include_router(people.router)
app.include_router(digest.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}

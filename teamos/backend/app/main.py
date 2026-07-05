import asyncio
import logging
import subprocess
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import digest, knowledge, people, projects, tasks
from app.services.markdown_store import _GIT_REPO

log = logging.getLogger(__name__)


async def _git_pull_loop():
    while True:
        await asyncio.sleep(60)
        try:
            subprocess.run(
                ["git", "pull"],
                cwd=_GIT_REPO, check=True, capture_output=True,
            )
        except subprocess.CalledProcessError as exc:
            log.warning("git pull failed: %s", exc.stderr.decode(errors="replace"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_git_pull_loop())
    yield
    task.cancel()


app = FastAPI(title="TeamOS API", lifespan=lifespan)

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

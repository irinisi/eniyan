import httpx

from config import API_BASE_URL


async def get_tasks(params: dict | None = None) -> list[dict]:
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        resp = await client.get("/api/tasks", params=params)
        resp.raise_for_status()
        return resp.json()


async def create_task(payload: dict) -> dict:
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        resp = await client.post("/api/tasks", json=payload)
        resp.raise_for_status()
        return resp.json()


async def update_task(task_id: str, payload: dict) -> dict:
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        resp = await client.patch(f"/api/tasks/{task_id}", json=payload)
        resp.raise_for_status()
        return resp.json()


async def delete_task(task_id: str) -> bool:
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        resp = await client.delete(f"/api/tasks/{task_id}")
        if resp.status_code == 404:
            return False
        resp.raise_for_status()
        return True


async def search_knowledge(query: str) -> list[dict]:
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        resp = await client.get("/api/knowledge", params={"q": query})
        resp.raise_for_status()
        return resp.json()

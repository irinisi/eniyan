from fastapi import APIRouter

from app.services.digest import build_daily_digest

router = APIRouter(prefix="/api/digest", tags=["digest"])


@router.get("")
def get_digest():
    return {"text": build_daily_digest()}

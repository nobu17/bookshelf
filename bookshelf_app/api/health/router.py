from pydantic import BaseModel
from sqlalchemy import text

from bookshelf_app.api.shared.custom_router import CustomRouter
from bookshelf_app.infra.db.database import get_session

router = CustomRouter()


class HealthResponse(BaseModel):
    status: str


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/health/db", response_model=HealthResponse)
def health_db() -> HealthResponse:
    for session in get_session():
        session.execute(text("SELECT 1"))
        return HealthResponse(status="ok")

    raise RuntimeError("failed to open database session")

from pydantic import BaseModel

from bookshelf_app.api.shared.custom_router import CustomRouter

router = CustomRouter()


class HealthResponse(BaseModel):
    status: str


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")

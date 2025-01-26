from fastapi import Depends, status
from pydantic import UUID4, BaseModel

from bookshelf_app.api.shared.custom_router import CustomRouter
from bookshelf_app.infra.dependencies import (
    get_admin_dependency,
    get_tag_service,
    get_user_dependency,
)

from .service import TagCreateAppModel, TagService, TagUpdateAppModel

router = CustomRouter()


class TagBaseModel(BaseModel):
    name: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "AWS",
                }
            ]
        }
    }


class TagCreateModel(TagBaseModel):
    pass


class TagUpdateModel(TagBaseModel):
    pass


class TagResponse(TagBaseModel):
    tag_id: UUID4

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "50f65802-a5db-43cf-9dfc-3d5aea11d5dc",
                    "name": "AWS",
                }
            ]
        }
    }


@router.get("/tags", response_model=list[TagResponse])
async def list_tags(
    tag_service: TagService = Depends(get_tag_service),
) -> list[TagResponse]:
    data_results: list[TagResponse] = []

    domain_results = tag_service.list()
    for res in domain_results:
        data_results.append(TagResponse(**vars(res)))

    return data_results


@router.post("/tags", response_model=TagResponse, dependencies=[Depends(get_user_dependency)])
async def create_tag(
    body: TagCreateModel,
    tag_service: TagService = Depends(get_tag_service),
) -> TagResponse:
    result = tag_service.create(TagCreateAppModel(**vars(body)))
    return TagResponse(**vars(result))


@router.put("/tags/{id}", response_model=TagResponse, dependencies=[Depends(get_admin_dependency)])
async def update_tag(
    id: UUID4,
    body: TagUpdateModel,
    tag_service: TagService = Depends(get_tag_service),
) -> TagResponse:
    result = tag_service.update(id, TagUpdateAppModel(**vars(body)))
    return TagResponse(**vars(result))


@router.delete("/tags/{id}", dependencies=[Depends(get_admin_dependency)], status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    id: UUID4,
    tag_service: TagService = Depends(get_tag_service),
):
    tag_service.delete(id)
    return

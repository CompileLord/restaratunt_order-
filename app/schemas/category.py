from __future__ import annotations
from pydantic import BaseModel, computed_field, ConfigDict
from typing import Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from app.schemas.product import ProductOutSchema

class CategoryOutSchema(BaseModel):
    id: int
    title: str
    image_url: Optional[str] = None 
    products: list["ProductOutSchema"] = None
    @computed_field
    @property
    def image_path(self) -> Optional[str]:
        if self.image_url:
            return f"http://localhost:8000/{self.image_url}"
        return None

    model_config = ConfigDict(from_attributes=True)


class CategoryDetailOutSchema(BaseModel):
    id: int
    title: str
    image_url: Optional[str] = None
    @computed_field
    @property
    def image_path(self) -> Optional[str]:
        if self.image_url:
            return f"http://localhost:8000/{self.image_url}"
        return None

    model_config = ConfigDict(from_attributes=True)


from app.schemas.product import ProductOutSchema
CategoryOutSchema.model_rebuild()
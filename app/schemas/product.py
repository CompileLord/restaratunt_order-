from pydantic import BaseModel, ConfigDict, computed_field, Field
from typing import Optional

class ProductBase(BaseModel):
    title: str
    description: str
    price: float
    category_id: int
    image_url: Optional[str] = None
    ingredients: Optional[str] = None
    discount_percent: int = 0

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    ingredients: Optional[str] = None
    discount_percent: Optional[int] = None
    is_active: Optional[bool] = None

class ProductOutSchema(ProductBase):
    id: int
    is_active: bool

    @computed_field
    @property
    def full_image_url(self) -> Optional[str]:
        if self.image_url:
            return f"http://localhost:8000/{self.image_url}"
        return None

    model_config = ConfigDict(from_attributes=True)
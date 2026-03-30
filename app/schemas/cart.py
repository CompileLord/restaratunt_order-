from pydantic import BaseModel, ConfigDict
from typing import Optional

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemUpdate(BaseModel):
    quantity: int

class ProductInCart(BaseModel):
    id: int
    title: str
    price: float
    image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class CartItemResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    product: ProductInCart

    model_config = ConfigDict(from_attributes=True)


from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    rating: int
    comment: Optional[str]

    model_config = ConfigDict(from_attributes=True)

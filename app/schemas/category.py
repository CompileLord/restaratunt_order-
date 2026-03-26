from pydantic import BaseModel, computed_field, ConfigDict
from typing import Optional

class CategoryOutSchema(BaseModel):
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

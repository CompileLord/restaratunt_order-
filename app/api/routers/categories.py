from fastapi import APIRouter, UploadFile, Depends
from sqlalchemy.orm import Session
from typing import List
from api.dependencies import get_db, get_current_user
from app.utils.services import save_images
from app.core.security import check_is_admin
from app.schemas.category import CategoryOutSchema
from app.crud.crud_category import (get_all_categories, get_by_id_category,
                                    create_category, check_available_category)


router = APIRouter()

@router.post("/add_category", response_model=CategoryOutSchema)
def add_category_view(
    title: str,
    description: str,
    image: UploadFile,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    check_is_admin(current_user=current_user,db=db)
    image_url = save_images(image)
    category = create_category(db=db, title=title, description=description, image_url=image_url)
    return category

@router.get("/get_all_categories", response_model=List[CategoryOutSchema])
def get_all_categories_view(db: Session = Depends(get_db)):
    return get_all_categories(db=db)

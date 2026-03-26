from fastapi import APIRouter, UploadFile, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import get_db, get_current_user
from app.utils.services import save_images
from app.api.dependencies import check_is_admin
from app.schemas.category import CategoryOutSchema, CategoryDetailOutSchema
from app.schemas.user import UserOutSchema
from app.crud.crud_category import (get_all_categories, get_by_id_category,
                                    create_category, check_available_category, delete_category)


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
    if not check_available_category(db=db, title=title):
        raise HTTPException(detail="Category with this title already exists", status_code=status.HTTP_400_BAD_REQUEST)
    image_url = save_images(image)
    category = create_category(db=db, title=title, description=description, image_url=image_url)
    return category

@router.get("/get_all_categories", response_model=List[CategoryOutSchema])
def get_all_categories_view(db: Session = Depends(get_db)):
    return get_all_categories(db=db)


@router.get("/get_category/{category_id}", response_model=CategoryOutSchema)
def get_by_id(category_id: int, current_user = Depends(get_current_user), db=Depends(get_db)):
    categories = get_by_id_category(db=db, category_id=category_id)
    return categories

@router.delete("/delete_category/{category_id}")
def delete_category_view(
    category_id: int, 
    admin: UserOutSchema = Depends(check_is_admin), 
    db: Session = Depends(get_db)
):
    category = get_by_id_category(category_id=category_id, db=db)
    if not category:
        raise HTTPException(detail="Category not found", status_code=status.HTTP_404_NOT_FOUND)
    success = delete_category(db=db, category_id=category_id)
    
    return {"message": "Category deleted successfully", "status_code": 200}


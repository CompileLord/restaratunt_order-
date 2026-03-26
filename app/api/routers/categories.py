from fastapi import APIRouter
from sqlalchemy.orm import Session
from api.dependencies import get_db, get_current_user
from app.crud.crud_category import (get_all_categories, get_by_id_category,
                                    create_category, check_available_category)


router = APIRouter()


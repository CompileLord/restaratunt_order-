from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.api.dependencies import get_db, get_current_user, check_is_admin
from app.db.models import User, Role
from app.schemas.user import UserOutSchema

router = APIRouter(prefix="/users", tags=["users"])

class UserUpdateSchema(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserRoleUpdateSchema(BaseModel):
    role: str

class UserAdminOutSchema(UserOutSchema):
    id: int
    role: str
    model_config = ConfigDict(from_attributes=True)

@router.get("/me", response_model=UserOutSchema)
def get_me(current_user=Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserOutSchema)
def update_me(user_update: UserUpdateSchema, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.phone is not None:
        current_user.phone = user_update.phone
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/", response_model=List[UserAdminOutSchema])
def list_users(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1), db: Session = Depends(get_db), admin=Depends(check_is_admin)):
    return db.query(User).offset(skip).limit(limit).all()

@router.patch("/{id}/role", response_model=UserAdminOutSchema)
def update_user_role(id: int, role_update: UserRoleUpdateSchema, db: Session = Depends(get_db), admin=Depends(check_is_admin)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        user.role = Role(role_update.role)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid role. Choose from: {[r.value for r in Role]}")

    db.commit()
    db.refresh(user)
    return user

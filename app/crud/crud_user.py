from sqlalchemy.orm import Session
from app.db.models import User, Role


def create_user(email: str, password: str, full_name: str, phone: str, role: Role, db: Session):
    new_user = User(email = email, password=password, full_name=full_name, phone=phone, role=role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user




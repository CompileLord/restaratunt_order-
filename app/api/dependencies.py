from app.db.database import SessionLocal
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.core.security import decode_payload
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.models import User, Role
from app.schemas.user import UserOutSchema
from app.core.security import decode_payload

def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

oauth2_scheme = HTTPBearer()

def get_current_user(db: Session = Depends(get_db), token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    user = decode_payload(db=db, token=token.credentials)
    return user

def check_is_admin(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No enough permission"
        )
    return current_user
     
    






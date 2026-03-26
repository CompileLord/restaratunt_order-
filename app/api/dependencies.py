from app.db.database import SessionLocal
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
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
     
    






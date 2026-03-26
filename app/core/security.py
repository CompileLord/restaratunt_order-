from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from datetime import datetime, timedelta
import jwt
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.schemas.token import TokenSchema, TokenData
from app.schemas.user import UserOutSchema
from app.db.models import User, TokenBlacklist, Role
from app.core.config import SECRET_KEY
from fastapi import Depends

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def is_token_blacklist(db: Session, token: str):
    return db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first() is not None

def blacklist_token(db: Session, token: str):
    db_token = TokenBlacklist(token=token)
    db.add(db_token)
    db.commit()

def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_tokens(email: str):
    access_token = create_token(
        {"sub": email},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_token(
        {"sub": email},
        timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    )
    return TokenSchema(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email==email).first()

def authenticate_user(db: Session, email: str, password: str):
    
    user = get_user_by_email(db=db, email=email)
    if not user or not verify_password(password, user.password):
        return None
    return user




def check_available_phone_or_email(db: Session, email: str, phone: str):
    return db.query(User).filter(or_(User.email == email, User.phone == phone)).first() is not None


def decode_payload(token: str, db: Session):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except jwt.ExpiredSignatureError:
        raise HTTPException(detail="Token has expired", status_code=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        raise credentials_exception
    
    if is_token_blacklist(db=db, token=token):
        raise HTTPException(detail="Token is blacklisted", status_code=status.HTTP_401_UNAUTHORIZED)
    
    user = get_user_by_email(db=db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user











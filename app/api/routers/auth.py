from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.core.security import  create_tokens, hash_password, check_available_phone_or_email, authenticate_user
from app.schemas.user import UserOutSchema, UserSchema, UserLoginSchema
from app.schemas.token import TokenSchema
from app.crud.crud_user import create_user
from api.dependencies import get_db, get_current_user
from app.db.models import Role, User, TokenBlacklist

auth_router = APIRouter()

oauth2 = HTTPBearer()

@auth_router.post("/register", response_model=UserOutSchema)
def register_view(body: UserSchema, db: Session = Depends(get_db)):
    check_email_phone = check_available_phone_or_email(db=db, email=body.email, phone=body.phone)
    if check_email_phone:
        raise HTTPException(detail="user with this email or phone already exists", status_code=status.HTTP_400_BAD_REQUEST)

    hashed_password = hash_password(body.password)
    user = create_user(db=db, email=body.email, password=hashed_password, full_name=body.full_name, phone=body.phone, role=Role.USER)
    return user


@auth_router.post("/login", response_model=TokenSchema)
def login_view(form: UserLoginSchema = Depends(), db: Session=Depends(get_db)):
    user = authenticate_user(db=db, email=form.email, password=form.password)
    if not user:
        raise HTTPException(detail="Invalid Credentials", status_code=status.HTTP_400_BAD_REQUEST)
    return create_tokens(user.email)

@auth_router.post("/logout")
def logout(current_user: User = Depends(get_current_user), token: HTTPAuthorizationCredentials = Depends(oauth2), db: Session = Depends(get_db)):
    token: str = token.credentials
    already_blacklisted = db.query(TokenBlacklist).filter(TokenBlacklist.token==token).first()
    if not already_blacklisted:
        new_blacklisted = TokenBlacklist(token=token)
        db.add(new_blacklisted)
        db.commit()
    return {"message": "Successfully logged out", "code": 200}

    

@auth_router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {"email": current_user.email, "full_name": current_user.full_name}
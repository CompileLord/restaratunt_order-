from pydantic import BaseModel

class UserSchema(BaseModel):
    email: str
    password: str
    full_name: str
    phone: str

class UserOutSchema(BaseModel):
    email: str
    full_name: str
    phone: str

class UserLoginSchema(BaseModel):
    email: str
    password: str


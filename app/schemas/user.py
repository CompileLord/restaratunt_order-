from pydantic import BaseModel, ConfigDict

class UserSchema(BaseModel):
    email: str
    password: str
    full_name: str
    phone: str

class UserOutSchema(BaseModel):
    email: str
    full_name: str
    phone: str
    model_config = ConfigDict(from_attributes=True)

class UserLoginSchema(BaseModel):
    email: str
    password: str


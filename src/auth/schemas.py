from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class UserCreateModel(BaseModel):
    username: str = Field(max_length=20)
    email: str = Field(max_length=30)
    password: str = Field(min_length=6)
    first_name: str
    last_name: str

class UserLoginModel(BaseModel):
    email: str
    password: str

class UserModel(BaseModel):
    uid: uuid.UUID 
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool 
    created_at: datetime 
    updated_at: datetime 

class UserLoginModel(BaseModel):
    email: str
    password: str

class ForgotPasswordModel(BaseModel):
    email: str

class ResetPasswordModel(BaseModel):
    token: str
    new_password: str
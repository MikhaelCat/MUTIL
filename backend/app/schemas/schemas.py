from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Task schemas
class TaskBase(BaseModel):
    text: str

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    created_at: datetime
    creator_id: Optional[int] = None

    class Config:
        from_attributes = True

# Response schemas
class ResponseBase(BaseModel):
    text: Optional[str] = None

class ResponseCreate(ResponseBase):
    task_id: int

class ResponseUpdate(ResponseBase):
    pass

class Response(ResponseBase):
    id: int
    created_at: datetime
    author_id: Optional[int] = None
    task_id: int
    image_path: Optional[str] = None

    class Config:
        from_attributes = True

# Vote schemas
class VoteBase(BaseModel):
    value: int  

class VoteCreate(VoteBase):
    response_id: int

class Vote(VoteBase):
    id: int
    created_at: datetime
    user_id: int
    response_id: int

    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# TopResponse schemas
class TopResponse(BaseModel):
    response_id: int
    score: float
    calculated_at: datetime

    class Config:
        from_attributes = True
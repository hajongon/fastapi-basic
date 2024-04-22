from pydantic import BaseModel
from datetime import datetime


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class Post(PostBase):
    # id: int
    title: str
    content: str
    published: bool
    created_at: datetime

    # class Config:
    #     from_attributes = True

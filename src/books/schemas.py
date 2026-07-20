from pydantic import BaseModel,ConfigDict
import uuid
from datetime import datetime, date
from src.reviews.schemas import ReviewResponseModel

class Book(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime
    updated_at: datetime

class BookCreateModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str

class BookUpdateModel(BaseModel):
    title: str | None = None
    author: str | None = None
    publisher: str | None = None
    page_count: int | None = None
    language: str | None = None

class BookDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    average_rating: float
    review_count: int
    
    reviews: list[ReviewResponseModel]

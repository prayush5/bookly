from sqlmodel import Field, Relationship
from datetime import date
import uuid
from typing import Optional
from src.db.models import AuditMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.reviews.models import Review

class Book(AuditMixin, table=True):
    __tablename__ = "books"

    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key='users.uid')

    reviews: list["Review"] = Relationship(back_populates="book")

    def __repr__(self):
        return f"<Book {self.title}> (ID: {self.uid})"
from sqlmodel import Field, Relationship
import uuid
from src.db.models import AuditMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.auth.models import User
    from src.books.models import Book

class Review(AuditMixin, table=True):

    rating: float
    comment: str

    user_uid: uuid.UUID = Field(foreign_key="users.uid")
    book_uid: uuid.UUID = Field(foreign_key="books.uid")

    user: "User" = Relationship(back_populates="reviews")
    book: "Book" = Relationship(back_populates="reviews")

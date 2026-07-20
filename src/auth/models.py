from sqlmodel import Field, Relationship
from src.db.models import AuditMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.reviews.models import Review

class User(AuditMixin, table=True):

    __tablename__ = 'users'

    username: str
    email: str
    password_hash: str = Field(exclude=True)
    first_name: str
    last_name: str

    role: str = Field(default="user", nullable=False)
    is_verified: bool = Field(default=False)

    reviews: list['Review'] = Relationship(back_populates="user")

    def __repr__(self):
        return f"<User {self.username} (ID: {self.uid})>"

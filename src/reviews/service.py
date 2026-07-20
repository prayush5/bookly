from src.reviews.schemas import ReviewCreateModel, ReviewUpdateModel
from sqlmodel.ext.asyncio.session import AsyncSession
import uuid
from .models import Review
from src.auth.models import User
from sqlmodel import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from src.errors import ReviewNotFound, NoFieldsToUpdate
from src.books.utils import invalidate_cache

class ReviewService:
    async def create_review(self, review_data: ReviewCreateModel, book_uid: uuid.UUID, user_uid: uuid.UUID, session: AsyncSession):
        review = Review(
            **review_data.model_dump(),
            user_uid = user_uid,
            book_uid = book_uid
            )
        
        session.add(review)
        await session.commit()

        await invalidate_cache(f"book:{str(book_uid)}")
        await session.refresh(review)

        return review
    
    async def update_review(self, book_uid: uuid.UUID, user_uid: uuid.UUID, review_data: ReviewUpdateModel, session: AsyncSession):
        review = await self.get_user_review_for_book(book_uid, user_uid, session)

        if review is None:
            raise ReviewNotFound()
        
        updated_review = review_data.model_dump(exclude_unset=True)

        if not updated_review:
            raise NoFieldsToUpdate()
        
        for key,value in updated_review.items():
            setattr(review, key, value)

        await session.commit()
        await invalidate_cache(f"book:{str(book_uid)}")
        await session.refresh(review)

        return review
    
    async def get_user_review_for_book(self, book_uid: uuid.UUID, user_uid: uuid.UUID, session: AsyncSession):
        statement = select(Review).where(
            Review.user_uid == user_uid,
            Review.book_uid == book_uid
        )

        result = await session.exec(statement)

        return result.first()
    
    
    async def get_review_for_book(self, book_uid: uuid.UUID, session: AsyncSession, limit: int, offset: int):
        statement = select(Review).options(selectinload(Review.user)).where(Review.book_uid == book_uid).offset(offset).limit(limit)
        result = await session.exec(statement)
        reviews = result.all()
        return [
            {
                "username": review.user.username,
                "rating": review.rating,
                "comment": review.comment
            }
            for review in reviews
        ]
    
    async def get_book_rating_stats(self, book_uid: uuid.UUID, session: AsyncSession):
        statement = select(
            func.avg(Review.rating),
            func.count(Review.uid)
        ).where(Review.book_uid == book_uid)

        result = await session.exec(statement)

        average_rating, review_count = result.one()

        return {
            "average_rating": float(average_rating) if average_rating else 0,
            "review_count": float(review_count)
        }

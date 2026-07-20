from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import BookCreateModel, BookUpdateModel
from sqlmodel import select, desc
from .models import Book
from src.reviews.models import Review
from sqlalchemy.orm import selectinload
from src.errors import NoFieldsToUpdate
from datetime import datetime
from sqlalchemy import or_, desc
from .utils import get_cached_data, set_cache_data, invalidate_cache
import uuid
from src.reviews.service import ReviewService

review_service = ReviewService()

class BookService:
    async def get_all_books(self, session:AsyncSession, limit: int, offset: int, search: str | None = None):
        statement = select(Book).where(Book.is_deleted == False)
        if search:
            statement = statement.where(
                or_(
                    Book.title.ilike(f"%{search}%"),
                    Book.author.ilike(f"%{search}%")
                )
            )
        
        statement = (
            statement.order_by(desc(Book.created_at))
            .offset(offset)
            .limit(limit)
        )

        result = await session.exec(statement)

        return result.all()
    
    async def get_user_books(self, user_uid: str, session:AsyncSession):
        statement = select(Book).where(Book.user_uid == user_uid, Book.is_deleted == False).order_by(desc(Book.created_at))

        result = await session.exec(statement)

        return result.all()
    

    async def get_book(self, book_uid: uuid.UUID, session:AsyncSession):

        statement = (
            select(Book)
            .where(Book.uid == book_uid, Book.is_deleted == False)
            .options(
                selectinload(
                    Book.reviews.and_(Review.is_deleted == False)
                ).selectinload(Review.user)
            )
        )

        result = await session.exec(statement)

        return result.first()
    
    async def get_book_details_payload(self, book_uid: uuid.UUID, session: AsyncSession):

        cache_key = f"book:{str(book_uid)}"

        # attempt cache lookup
        cached_data = await get_cached_data(cache_key)

        if cached_data:
            return cached_data
        
        #cache miss
        book = await self.get_book(book_uid, session)

        if not book:
            return None
        
        stats = await review_service.get_book_rating_stats(book_uid, session)

        #serializer safe dict
        serialized_reviews = [
            {**review.model_dump(), "user": review.user.model_dump()}
            for review in book.reviews
        ] if book.reviews else []

        payload =  {
            **book.model_dump(),
            "average_rating": stats['average_rating'],
            "review_count": stats['review_count'],
            "reviews": serialized_reviews
        }

        await set_cache_data(cache_key, payload, expire=3600)

        return payload

    async def create_book(self, book_data: BookCreateModel, user_uid: str, session:AsyncSession):
        book_data_dict = book_data.model_dump()

        new_book = Book(
            **book_data_dict
        )

        new_book.user_uid = user_uid

        session.add(new_book)

        await session.commit()
        await invalidate_cache(f"book:{str(new_book.uid)}")

        return new_book


    async def update_book(self, book_uid: uuid.UUID, update_data: BookUpdateModel, session:AsyncSession):
        book_to_update = await self.get_book(book_uid, session)

        if book_to_update is not None:
            update_data_dict = update_data.model_dump(exclude_unset=True)

            if not update_data_dict:
                raise NoFieldsToUpdate()

            for k, v in update_data_dict.items():
                setattr(book_to_update, k, v)

            await session.commit()

            await invalidate_cache(f"book:{str(book_uid)}")

            return book_to_update
        
        return None


    async def delete_book(self, book_uid: uuid.UUID, session:AsyncSession):
        book_to_delete = await self.get_book(book_uid, session)

        if book_to_delete is not None:
            book_to_delete.is_deleted = True

            book_to_delete.deleted_at = datetime.now()

            session.add(book_to_delete)

            await session.commit()
            await invalidate_cache(f"book:{str(book_uid)}")

            return True
        return None
        
        
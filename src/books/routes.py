from fastapi import APIRouter, status, Depends, Request
from .book_data import books
from .schemas import Book, BookUpdateModel, BookCreateModel, BookDetailResponse
from typing import List
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.service import BookService
from src.auth.dependencies import TokenValidator, RoleChecker
import uuid
from src.reviews.schemas import ReviewCreateModel, ReviewUpdateModel, ReviewResponseModel
from src.reviews.service import ReviewService
from src.errors import BookNotFound, ReviewExists, ReviewNotFound
from src.middleware import limiter, get_user_jwt
import structlog

logger = structlog.get_logger(__name__)
book_router = APIRouter()
book_service = BookService()
review_service = ReviewService()
access_token_bearer = TokenValidator()
user_or_admin = Depends(RoleChecker(['admin', 'user']))
admin_only = Depends(RoleChecker(['admin']))

@book_router.get('/', response_model=List[Book], status_code=status.HTTP_200_OK, dependencies=[user_or_admin])
@limiter.limit("50/minute", key_func=get_user_jwt)
async def get_all_books(request: Request, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer), page: int = 1, limit: int = 10, search: str | None = None):
    offset = (page - 1) * limit
    books = await book_service.get_all_books(session, limit, offset, search)
    return books

@book_router.get('/user/{user_uid}', response_model=List[Book], status_code=status.HTTP_200_OK, dependencies=[user_or_admin])
@limiter.limit("50/minute", key_func=get_user_jwt)
async def get_user_book_submissions(request: Request, user_uid: str, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):
    books = await book_service.get_user_books(user_uid, session)
    return books

@book_router.post('/', status_code=status.HTTP_201_CREATED, response_model=Book, dependencies=[admin_only])
@limiter.limit("10/minute", key_func=get_user_jwt)
async def create_a_book(request: Request, book_data: BookCreateModel, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):
    user_id = token_details.get('user')['user_uid']
    new_book = await book_service.create_book(book_data, user_id, session)
    return new_book

@book_router.get('/{book_uid}', status_code=status.HTTP_200_OK, response_model=BookDetailResponse, dependencies=[user_or_admin])
@limiter.limit("50/minute", key_func=get_user_jwt)
async def get_book(request: Request, book_uid: uuid.UUID, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)) -> dict:
    logger.info("fetching book details", book_uid=book_uid)
    book = await book_service.get_book_details_payload(book_uid, session)

    if not book:
        raise BookNotFound()
    
    return book

@book_router.patch('/{book_uid}', status_code=status.HTTP_200_OK, response_model=Book, dependencies=[admin_only])
@limiter.limit("50/minute", key_func=get_user_jwt)
async def update_book(request: Request, book_uid: uuid.UUID, book_update_data: BookUpdateModel, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):
    updated_book = await book_service.update_book(book_uid, book_update_data, session)
    
    if updated_book:
        return updated_book
    else:
        raise BookNotFound()

@book_router.delete('/{book_uid}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[admin_only])
@limiter.limit("50/minute", key_func=get_user_jwt)
async def delete_book(request: Request, book_uid: uuid.UUID, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)) -> None:
    book_to_delete = await book_service.delete_book(book_uid, session)

    if book_to_delete:
        return None
    else:
        raise BookNotFound()
    
@book_router.post('/{book_uid}/reviews', status_code=status.HTTP_201_CREATED, dependencies=[user_or_admin])
@limiter.limit("5/minute", key_func=get_user_jwt)
async def create_a_review(request: Request, book_uid: uuid.UUID, review_data: ReviewCreateModel, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):
    user_uid = token_details['user']['user_uid']

    existing_review = await review_service.get_user_review_for_book(book_uid, user_uid, session)

    if existing_review:
        raise ReviewExists()
    
    review = await review_service.create_review(review_data, book_uid, user_uid, session)
    return review    

@book_router.get('/{book_uid}/reviews', dependencies=[user_or_admin], response_model=List[ReviewResponseModel])
@limiter.limit("50/minute", key_func=get_user_jwt)
async def get_review_for_a_book(request: Request, book_uid: uuid.UUID, session: AsyncSession =  Depends(get_session), page: int = 1, limit: int = 10):
    offset = (page - 1) * limit
    return await review_service.get_review_for_book(book_uid, session, limit, offset)

@book_router.patch('/{book_uid}/reviews', status_code=status.HTTP_200_OK, dependencies=[user_or_admin], response_model=ReviewResponseModel)
@limiter.limit("5/minute", key_func=get_user_jwt)
async def update_a_review(request: Request, book_uid: uuid.UUID, review_data: ReviewUpdateModel, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):
    user_uid = token_details['user']['user_uid']

    review = await review_service.update_review(user_uid, book_uid, review_data, session)

    if review is None:
        raise ReviewNotFound()

    return review
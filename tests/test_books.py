from datetime import date, datetime
from types import SimpleNamespace
import uuid
import pytest

from fastapi.testclient import TestClient

from src import app
from src.auth import dependencies as auth_dependencies
from src.auth import routes as auth_routes
from src.books import routes as book_routes
from src.db.main import get_session


async def override_get_session():
    yield SimpleNamespace()

@pytest.fixture
def auth_client(monkeypatch):
    admin_uid = uuid.uuid4()
    admin_user = SimpleNamespace(
        uid=admin_uid,
        username="admin",
        email="admin@example.com",
        password_hash="hashed-password",
        first_name="Admin",
        last_name="User",
        role="admin",
        is_verified=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    async def get_user_by_email(email, session):
        return admin_user

    async def get_current_admin_user():
        return admin_user

    async def token_not_in_blocklist(jti):
        return False
    
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[auth_dependencies.get_current_user] = get_current_admin_user

    monkeypatch.setattr(auth_routes.user_service, "get_user_by_email", get_user_by_email)
    monkeypatch.setattr(auth_routes, "verify_password", lambda password, password_hash: True)
    monkeypatch.setattr(auth_dependencies, "token_in_blocklist", token_not_in_blocklist)

    client = TestClient(app)
    login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "admin@example.com",
                "password": "password123",
            },
        )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"] 

    client.headers.update({"Authorization": f"Bearer {access_token}"})   

    yield client

    app.dependency_overrides.clear()

def test_admin_user_can_create_book(auth_client, monkeypatch):                         
    async def create_book(book_data, user_uid, session):
        return {
            "uid": uuid.uuid4(),
            "title": book_data.title,
            "author": book_data.author,
            "publisher": book_data.publisher,
            "published_date": book_data.published_date,
            "page_count": book_data.page_count,
            "language": book_data.language,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
    
    monkeypatch.setattr(book_routes.book_service, "create_book", create_book)

    create_book_response = auth_client.post(
            "/api/v1/books/",
            json={
                "title": "Clean Architecture",
                "author": "Robert C. Martin",
                "publisher": "Prentice Hall",
                "published_date": date(2017, 9, 20).isoformat(),
                "page_count": 432,
                "language": "English",
            },
        )
    
    assert create_book_response.status_code == 201
    created_book = create_book_response.json()
    assert created_book["title"] == "Clean Architecture"
    assert created_book["author"] == "Robert C. Martin"
    assert created_book["language"] == "English"

def test_admin_user_can_update_book(auth_client, monkeypatch):
    book_uid = uuid.uuid4()

    async def update_book(book_id, book_data, session):
        return { 
            "uid": book_id,
            "title": book_data.title,
            "author": book_data.author,
            "publisher": "Prentice Hall",
            "published_date": date(2017, 9, 20),
            "page_count": 432,
            "language": "English",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
    monkeypatch.setattr(book_routes.book_service, "update_book", update_book)
    
    response = auth_client.patch(
        f"/api/v1/books/{book_uid}", 
        json={
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "publisher": "Prentice Hall",
            "page_count": 432,
            "language": "English"
        }
    )

    assert response.status_code == 200
    updated_book = response.json()

    assert updated_book["title"] == "Clean Code"
    assert updated_book["author"] == "Robert C. Martin"
    assert updated_book["publisher"] == "Prentice Hall"
    assert updated_book["page_count"] == 432
    assert updated_book["language"] == "English"


def test_admin_user_can_delete_book(auth_client, monkeypatch):
    book_uid = uuid.uuid4()

    async def delete_book(book_uid_param, session):
        return True
    
    monkeypatch.setattr(book_routes.book_service, "delete_book", delete_book)

    response = auth_client.delete(f"/api/v1/books/{book_uid}")

    assert response.status_code == 204
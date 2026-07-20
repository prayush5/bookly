from fastapi.testclient import TestClient

from src import app


def test_openapi_schema_includes_book_and_auth_routes():
    client = TestClient(app)

    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/v1/auth/login" in paths
    assert "/api/v1/books/" in paths
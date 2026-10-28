
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.main import app, get_db


# Create an isolated, in-memory SQLite database for testing.
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


# Give the API a test database session instead of PostgreSQL.
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app, follow_redirects=False) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


def test_create_short_url(client):
    response = client.post(
        "/api/urls",
        json={"original_url": "https://www.python.org/"},
    )

    assert response.status_code == 201

    data = response.json()
    assert len(data["short_code"]) == 7
    assert data["short_url"].endswith("/" + data["short_code"])


def test_redirect_to_original_url(client):
    create_response = client.post(
        "/api/urls",
        json={"original_url": "https://www.python.org/"},
    )

    short_code = create_response.json()["short_code"]

    response = client.get(f"/{short_code}")

    assert response.status_code == 302
    assert response.headers["location"] == "https://www.python.org/"


def test_unknown_short_code_returns_404(client):
    response = client.get("/doesnotexist")

    assert response.status_code == 404


def test_invalid_url_returns_422(client):
    response = client.post(
        "/api/urls",
        json={"original_url": "not-a-valid-url"},
    )

    assert response.status_code == 422

import pytest
import httpx
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = 'postgresql://postgres:web66@postgres/postgres'
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_movie(setup_db):
    with httpx.Client(base_url="http://kong:8000/inventory-service") as client:
        response = client.post("/movies", json={"name": "Inception", "available_seats": 100})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Inception"
        assert data["available_seats"] == 100


def test_read_movie(setup_db):
    with httpx.Client(base_url="http://kong:8000/inventory-service") as client:
        response = client.get("/movies/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Inception"


def test_update_movie(setup_db):
    with httpx.Client(base_url="http://kong:8000/inventory-service") as client:
        response = client.put("/movies/1", json={"name": "Inception", "available_seats": 80})
        assert response.status_code == 200
        data = response.json()
        assert data["available_seats"] == 80


def test_book_tickets(setup_db):
    with httpx.Client(base_url="http://kong:8000/booking-service") as client:
        response = client.post("/book/", params={"movie_id": 1, "quantity": 10})
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Tickets successfully booked"


def test_book_tickets_fail(setup_db):
    with httpx.Client(base_url="http://kong:8000/booking-service") as client:
        response = client.post("/book/", params={"movie_id": 1, "quantity": 1000})
        assert response.status_code == 400
        assert response.json()["detail"] == {'detail': 'Not enough available seats'}


def test_delete_movie(setup_db):
    with httpx.Client(base_url="http://kong:8000/inventory-service") as client:
        response = client.delete("/movies/1")
        assert response.status_code == 200
        assert response.json() == {"message": "Successfully Deleted!"}

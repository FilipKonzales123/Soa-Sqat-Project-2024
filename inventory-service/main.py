from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List

DATABASE_URL = 'postgresql://postgres:web66@postgres/postgres'
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()


class Movie(Base):
    __tablename__ = 'movies'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    available_seats = Column(Integer)


Base.metadata.create_all(bind=engine)


class MovieCreate(BaseModel):
    name: str
    available_seats: int


class MovieResponse(BaseModel):
    id: int
    name: str
    available_seats: int

    class Config:
        orm_mode = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/movies", response_model=MovieResponse)
def create_movie(movie: MovieCreate, db: SessionLocal = Depends(get_db)):
    db_movie = Movie(name=movie.name, available_seats=movie.available_seats)
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


@app.get("/movies/{movie_id}", response_model=None)
def read_movie(movie_id: int, db: SessionLocal = Depends(get_db)):
    return db.query(Movie).filter(Movie.id == movie_id).first()


@app.put("/movies/{movie_id}", response_model=MovieResponse)
def update_movie(movie_id: int, mov: MovieCreate, db: SessionLocal = Depends(get_db)):
    db_getmovie = db.query(Movie).filter(Movie.id == movie_id).first()
    db_getmovie.name = mov.name
    db_getmovie.available_seats = mov.available_seats
    db.commit()
    return db_getmovie


@app.delete("/movies/{movie_id}", response_model=None)
def delete_movie(movie_id: int, db: SessionLocal = Depends(get_db)):
    db_getmovie = db.query(Movie).filter(Movie.id == movie_id).first()
    db.delete(db_getmovie)
    db.commit()
    return {"message": "Successfully Deleted!"}


@app.get("/", response_model=List[MovieResponse])
def root(db: SessionLocal = Depends(get_db)):
    return db.query(Movie).all()


# this communicates with ./booking-service/test_main.py
@app.put("/movies/{movie_id}/book", response_model=MovieResponse)
def book_movie(movie_id: int, tickets: int, db: SessionLocal = Depends(get_db)):
    db_movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    if db_movie.available_seats < tickets:
        raise HTTPException(status_code=400, detail="Not enough available seats")
    db_movie.available_seats -= tickets
    db.commit()
    db.refresh(db_movie)
    return db_movie

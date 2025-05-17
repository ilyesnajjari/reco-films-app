from fastapi import FastAPI, Depends, HTTPException, Body
from sqlalchemy.orm import Session
import models, schemas, database

app = FastAPI()

database.Base.metadata.create_all(bind=database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_populate_movies():
    db = database.SessionLocal()
    try:
        if db.query(models.Movie).count() == 0:
            movies = [
                    models.Movie(
        title="Inception",
        genre="Sci-Fi",
        year=2010,
        description="A mind-bending thriller",
        average_rating=0.0,
        director="Christopher Nolan"
    ),
    models.Movie(
        title="The Matrix",
        genre="Sci-Fi",
        year=1999,
        description="Reality is an illusion",
        average_rating=0.0,
        director="Lana Wachowski, Lilly Wachowski"
    ),
    models.Movie(
        title="Interstellar",
        genre="Sci-Fi",
        year=2014,
        description="Space exploration",
        average_rating=0.0,
        director="Christopher Nolan"
    ),
    models.Movie(
        title="The Dark Knight",
        genre="Action",
        year=2008,
        description="Batman faces the Joker",
        average_rating=0.0,
        director="Christopher Nolan"
    ),
    models.Movie(
        title="Pulp Fiction",
        genre="Crime",
        year=1994,
        description="Interwoven stories in LA",
        average_rating=0.0,
        director="Quentin Tarantino"
    ),
    models.Movie(
        title="Forrest Gump",
        genre="Drama",
        year=1994,
        description="Life is like a box of chocolates",
        average_rating=0.0,
        director="Robert Zemeckis"
    ),
    models.Movie(
        title="The Shawshank Redemption",
        genre="Drama",
        year=1994,
        description="Hope can set you free",
        average_rating=0.0,
        director="Frank Darabont"
    ),
    models.Movie(
        title="Fight Club",
        genre="Drama",
        year=1999,
        description="An underground fight club",
        average_rating=0.0,
        director="David Fincher"
    ),
    models.Movie(
        title="The Godfather",
        genre="Crime",
        year=1972,
        description="The aging patriarch of an organized crime dynasty transfers control",
        average_rating=0.0,
        director="Francis Ford Coppola"
    ),
    models.Movie(
        title="The Lord of the Rings: The Fellowship of the Ring",
        genre="Fantasy",
        year=2001,
        description="A hobbit begins a perilous journey",
        average_rating=0.0,
        director="Peter Jackson"
)
        ]

            db.add_all(movies)
            db.commit()
    finally:
        db.close()

@app.get("/")
def root():
    return {
        "message": "Bienvenue sur l'API Movie Service",
        "endpoints": ["/movies/", "/movies/{movie_id}"]
    }

@app.post("/movies/", response_model=schemas.Movie)
def create_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    db_movie = models.Movie(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

@app.get("/movies/{movie_id}", response_model=schemas.Movie)
def read_movie(movie_id: int, db: Session = Depends(get_db)):
    db_movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return db_movie

@app.get("/movies/", response_model=list[schemas.Movie])
def read_movies(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(models.Movie).offset(skip).limit(limit).all()

@app.put("/movies/{movie_id}", response_model=schemas.Movie)
def update_movie(movie_id: int, movie: schemas.MovieUpdate, db: Session = Depends(get_db)):
    db_movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    update_data = movie.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_movie, key, value)
    db.commit()
    db.refresh(db_movie)
    return db_movie

@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    db_movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    db.delete(db_movie)
    db.commit()
    return {"detail": "Movie deleted"}



@app.put("/movies/{movie_id}/rating")
def update_movie_rating(movie_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    average_rating = data.get("average_rating")
    if average_rating is None:
        raise HTTPException(status_code=400, detail="Missing average_rating")

    movie.average_rating = average_rating
    db.commit()
    return {"message": "Average rating updated", "average_rating": average_rating}

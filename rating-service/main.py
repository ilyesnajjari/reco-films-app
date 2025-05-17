import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, database
import httpx
from typing import Optional


app = FastAPI()

database.Base.metadata.create_all(bind=database.engine)

# Récupérer les URLs des services depuis les variables d'environnement
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8002")
MOVIE_SERVICE_URL = os.getenv("MOVIE_SERVICE_URL", "http://localhost:8001")

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API Rating Service"}

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/ratings/", response_model=schemas.Rating)
def create_rating(rating: schemas.RatingCreate, db: Session = Depends(get_db)):
    # Vérifier que l'utilisateur existe via USER_SERVICE_URL
    try:
        user_response = httpx.get(f"{USER_SERVICE_URL}/users/{rating.user_id}")
        user_response.raise_for_status()
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=400, detail="User not found")

    # Vérifier que le film existe via MOVIE_SERVICE_URL
    try:
        movie_response = httpx.get(f"{MOVIE_SERVICE_URL}/movies/{rating.movie_id}")
        movie_response.raise_for_status()
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=400, detail="Movie not found")

    # Créer la note en base
    db_rating = models.Rating(**rating.dict())
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)

    # Recalculer la moyenne des notes pour ce film
    ratings_for_movie = db.query(models.Rating).filter(models.Rating.movie_id == rating.movie_id).all()
    average_rating = sum(r.rating for r in ratings_for_movie) / len(ratings_for_movie)

    # Mettre à jour la moyenne dans le movie-service
    try:
        update_payload = {"average_rating": average_rating}
        update_response = httpx.put(
    f"{MOVIE_SERVICE_URL}/movies/{rating.movie_id}/rating",
    json=update_payload,
)

        update_response.raise_for_status()
    except httpx.HTTPError as e:
        print(f"Erreur lors de la mise à jour de la moyenne dans movie-service : {e}")

    return db_rating




@app.get("/ratings/", response_model=list[schemas.Rating])
def read_ratings(user_id: Optional[int] = None, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    query = db.query(models.Rating)
    if user_id is not None:
        query = query.filter(models.Rating.user_id == user_id)
    ratings = query.offset(skip).limit(limit).all()
    return ratings




@app.delete("/ratings/{rating_id}")
def delete_rating(rating_id: int, db: Session = Depends(get_db)):
    db_rating = db.query(models.Rating).filter(models.Rating.id == rating_id).first()
    if not db_rating:
        raise HTTPException(status_code=404, detail="Rating not found")

    movie_id = db_rating.movie_id  # On récupère l'ID du film avant suppression
    db.delete(db_rating)
    db.commit()

    # Recalcul de la moyenne après suppression
    remaining_ratings = db.query(models.Rating).filter(models.Rating.movie_id == movie_id).all()
    average_rating = (
        sum(r.rating for r in remaining_ratings) / len(remaining_ratings)
        if remaining_ratings else 0.0
    )

    # Mise à jour dans movie-service
    try:
        update_payload = {"average_rating": average_rating}
        update_response = httpx.put(
            f"{MOVIE_SERVICE_URL}/movies/{movie_id}/rating",
            json=update_payload,
        )
        update_response.raise_for_status()
    except httpx.HTTPError as e:
        print(f"Erreur lors de la mise à jour de la moyenne après suppression : {e}")

    return {"detail": "Rating deleted", "new_average": average_rating}

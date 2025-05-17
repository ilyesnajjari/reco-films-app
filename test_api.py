import pytest
import httpx
import os

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8002")
MOVIE_SERVICE_URL = os.getenv("MOVIE_SERVICE_URL", "http://localhost:8001")
RATING_SERVICE_URL = os.getenv("RATING_SERVICE_URL", "http://localhost:8003")

@pytest.fixture(scope="module")
def test_user():
    # Création d'un utilisateur de test
    response = httpx.post(f"{USER_SERVICE_URL}/users/", json={
        "username": "Test User",
        "email": "test@example.com",
        "password": "testpass"
    })
    assert response.status_code in [200, 201, 400, 409], f"User creation failed: {response.text}"

    # Récupération liste utilisateurs
    users_response = httpx.get(f"{USER_SERVICE_URL}/users/")
    assert users_response.status_code == 200
    users = users_response.json()

    user = next((u for u in users if u["email"] == "test@example.com"), None)
    assert user is not None, "User test@example.com not found after creation"
    return user

@pytest.fixture(scope="module")
def test_movie():
    # Création d'un film test
    response = httpx.post(f"{MOVIE_SERVICE_URL}/movies/", json={
        "title": "Test Movie",
        "genre": "Test",
        "year": 2025,
        "description": "Just a test",
        "director": "Tester"
    })
    assert response.status_code == 200, f"Movie creation failed: {response.text}"
    return response.json()

def test_create_rating_and_update_average(test_user, test_movie):
    # Création d'une note pour le film par l'utilisateur
    response = httpx.post(f"{RATING_SERVICE_URL}/ratings/", json={
        "user_id": test_user["id"],
        "movie_id": test_movie["id"],
        "rating": 4
    })
    assert response.status_code == 200, f"Rating creation failed: {response.text}"
    rating = response.json()
    assert rating["rating"] == 4

    # Vérifier que la moyenne dans movie-service a bien été mise à jour
    movie_response = httpx.get(f"{MOVIE_SERVICE_URL}/movies/{test_movie['id']}")
    assert movie_response.status_code == 200
    updated_movie = movie_response.json()
    assert updated_movie["average_rating"] == 4.0

def test_rating_history(test_user):
    response = httpx.get(f"{RATING_SERVICE_URL}/ratings/?user_id={test_user['id']}")
    assert response.status_code == 200
    ratings = response.json()
    assert isinstance(ratings, list)
    assert any(r["user_id"] == test_user["id"] for r in ratings)

def test_delete_rating_and_reset_average(test_movie):
    # Récupérer toutes les notes pour le film
    all_ratings_response = httpx.get(f"{RATING_SERVICE_URL}/ratings/")
    assert all_ratings_response.status_code == 200
    all_ratings = all_ratings_response.json()

    for rating in all_ratings:
        if rating["movie_id"] == test_movie["id"]:
            delete_response = httpx.delete(f"{RATING_SERVICE_URL}/ratings/{rating['id']}")
            assert delete_response.status_code == 200

    # Vérifier que la moyenne est bien remise à 0.0
    movie_response = httpx.get(f"{MOVIE_SERVICE_URL}/movies/{test_movie['id']}")
    assert movie_response.status_code == 200
    updated_movie = movie_response.json()
    assert updated_movie["average_rating"] == 0.0

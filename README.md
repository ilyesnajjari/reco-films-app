# 🎬 Reco Films App

Reco Films App est une application de recommandation de films basée sur une architecture microservices. Elle permet aux utilisateurs de s’inscrire, de noter des films, de consulter des recommandations et d’interagir avec une interface web moderne.

---

## 🏗️ Architecture

Le projet est composé de plusieurs microservices :

- **user-service** : gestion des utilisateurs (inscription, authentification, liste, suppression)
- **movie-service** : gestion des films (ajout, modification, consultation, calcul de la moyenne des notes)
- **rating-service** : gestion des notes attribuées par les utilisateurs aux films
- **frontend** : interface utilisateur (Streamlit)
- **postgres** : base de données relationnelle partagée

Chaque service possède son propre Dockerfile et peut être déployé via Docker Compose ou Kubernetes (Minikube).

---

## 🚀 Lancement rapide

### Prérequis

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- (Optionnel) [Minikube](https://minikube.sigs.k8s.io/) pour le déploiement Kubernetes
- [Python 3.10+](https://www.python.org/) pour le développement local

### Lancement avec Docker Compose

```bash
docker compose up --build
```

- **Frontend** accessible sur [http://localhost:8501](http://localhost:8501)
- **user-service** : [http://localhost:8002/users/](http://localhost:8002/users/)
- **movie-service** : [http://localhost:8001/movies/](http://localhost:8001/movies/)
- **rating-service** : [http://localhost:8003/ratings/](http://localhost:8003/ratings/)

### Lancement avec Kubernetes (Minikube)

```bash
cd k8s
./deploy.sh
```

Le script attend que tous les pods soient prêts et fait le port-forward automatiquement.

---

## 📦 Structure du projet

```
reco-films-app/
│
├── user-service/         # Microservice utilisateurs (FastAPI)
├── movie-service/        # Microservice films (FastAPI)
├── rating-service/       # Microservice notes (FastAPI)
├── frontend/             # Interface utilisateur (Streamlit)
├── k8s/                  # Manifests Kubernetes + script de déploiement
├── tests/                # Tests d’intégration (pytest, httpx)
├── docker-compose.yml    # Orchestration Docker Compose
├── .github/workflows/    # Pipelines CI/CD GitHub Actions
├── .gitignore
├── README.md
└── ...
```

---

## 🧪 Tests

Des tests d’intégration sont disponibles dans `test_api.py` :

```bash
pytest test_api.py
```

Ils vérifient la création d’utilisateurs, de films, de notes, la mise à jour des moyennes et la suppression.

---

## ⚙️ CI

Le pipeline GitHub Actions :

- Build les images Docker de chaque service
- Exécute les tests d’intégration (pytest, httpx) pour valider le bon fonctionnement des APIs

À chaque push ou pull request sur `main`, le pipeline vérifie que le projet se build et que les tests passent.

---

## 📝 Endpoints principaux

### user-service

- `POST /users/` : créer un utilisateur
- `GET /users/` : lister les utilisateurs
- `GET /users/{user_id}` : infos utilisateur
- `DELETE /users/{user_id}` : supprimer un utilisateur

### movie-service

- `POST /movies/` : ajouter un film
- `GET /movies/` : lister les films
- `GET /movies/{movie_id}` : infos film
- `PUT /movies/{movie_id}` : modifier un film

### rating-service

- `POST /ratings/` : ajouter une note
- `GET /ratings/` : lister les notes (filtrage possible)
- `DELETE /ratings/{rating_id}` : supprimer une note

---

## 🛠️ Développement

Chaque service est un projet Python indépendant (FastAPI ou Streamlit).  
Pour développer localement :

```bash
cd user-service
uvicorn main:app --reload --port 8000
```

Idem pour les autres services (adapter le port).

---

## 🙏 Remerciements

Projet pédagogique d’architecture microservices, orchestré avec Docker/Kubernetes, CI/CD GitHub Actions.

---


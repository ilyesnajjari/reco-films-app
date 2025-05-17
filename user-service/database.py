import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("La variable d'environnement DATABASE_URL n'est pas définie")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


#docker build -t ilyesnajjari/movie-service:latest ./movie-service
#docker push ilyesnajjari/movie-service:latest
#kubectl rollout restart deployment movie-service
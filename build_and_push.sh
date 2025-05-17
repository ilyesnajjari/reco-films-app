#!/bin/bash

# Ton nom Docker Hub
DOCKER_USERNAME="ilyesnajjari"

# Liste des services à builder
SERVICES=("user-service" "movie-service" "rating-service" "frontend")

for SERVICE in "${SERVICES[@]}"
do
  echo "🚀 Construction de l’image pour $SERVICE..."
  docker build -t $DOCKER_USERNAME/$SERVICE:latest ./$SERVICE

  echo "📤 Envoi de $SERVICE sur Docker Hub..."
  docker push $DOCKER_USERNAME/$SERVICE:latest
done

echo "✅ Tous les services ont été buildés et poussés avec succès."


#chmod +x build_and_push.sh
#./build_and_push.sh

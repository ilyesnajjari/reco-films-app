#!/bin/bash

set -e

echo "🚀 Lancement du build et push des images Docker..."
./build_and_push.sh

if [ $? -eq 0 ]; then
  echo "✅ Build & push réussi, lancement du déploiement Kubernetes..."
  cd k8s
  ./deploy.sh
else
  echo "❌ Échec du build & push, déploiement annulé."
  exit 1
fi

#chmod +x deploy_all.sh
#./deploy_all.sh
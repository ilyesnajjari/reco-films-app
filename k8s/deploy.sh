#!/bin/bash

set -e

NAMESPACE="default"
SERVICES_DIR="."

GREEN="\e[32m"
YELLOW="\e[33m"
BLUE="\e[34m"
RED="\e[31m"
RESET="\e[0m"

PORTS=(8000 8001 8002 8003 8501)
SERVICES=("postgres" "user-service" "movie-service" "rating-service" "frontend")

log() { echo -e "${BLUE}▶ $1${RESET}"; }
success() { echo -e "${GREEN}✔ $1${RESET}"; }
warn() { echo -e "${YELLOW}⚠ $1${RESET}"; }
error() { echo -e "${RED}✖ $1${RESET}"; }

wait_for_pod_ready() {
  local label=$1
  log "⏳ Attente que le pod app=$label soit en état Running et Ready..."

  for i in {1..30}; do
    POD_NAME=$(kubectl get pods -l app=$label -o jsonpath="{.items[0].metadata.name}" 2>/dev/null || echo "")
    POD_STATUS=$(kubectl get pod "$POD_NAME" -o jsonpath="{.status.phase}" 2>/dev/null || echo "")
    CONDITION=$(kubectl get pod "$POD_NAME" -o jsonpath="{.status.conditions[?(@.type=='Ready')].status}" 2>/dev/null || echo "")

    if [[ "$POD_STATUS" == "Running" && "$CONDITION" == "True" ]]; then
      success "$label est prêt."

      # Vérification spécifique Postgres avec pg_isready
      if [[ "$label" == "postgres" ]]; then
        for j in {1..10}; do
          if kubectl exec "$POD_NAME" -- pg_isready -U user &>/dev/null; then
            success "Postgres accepte les connexions."
            return
          fi
          sleep 1
          warn "pg_isready en attente... tentative $j"
        done
        error "pg_isready a échoué même si le pod est prêt."
        exit 1
      fi

      return
    fi

    sleep 2
    warn "$label non prêt... tentative $i"
  done

  error "$label n'est pas prêt après 60s."
  exit 1
}

log "🚀 Lancement de Minikube..."
# minikube start  # décommenter si nécessaire

CLUSTER_IP=$(minikube ip)

# Déploiement de Postgres
log "📦 Déploiement de Postgres..."
kubectl apply -f "$SERVICES_DIR/postgres/deployment.yaml"
kubectl apply -f "$SERVICES_DIR/postgres/service.yaml"

# Attente de Postgres prêt
wait_for_pod_ready "postgres"

# Déploiement des autres services
for SERVICE in "${SERVICES[@]:1}"; do
  log "📦 Déploiement de $SERVICE..."
  kubectl apply -f "$SERVICES_DIR/$SERVICE/deployment.yaml"
  kubectl apply -f "$SERVICES_DIR/$SERVICE/service.yaml"
done

# Attente que tous les pods soient prêts
for SERVICE in "${SERVICES[@]:1}"; do
  wait_for_pod_ready "$SERVICE"
done

# Port-forward automatique
log "🔌 Lancement des tunnels avec kubectl port-forward..."

INDEX=0
for SERVICE in "${SERVICES[@]}"; do
  LOCAL_PORT=${PORTS[$INDEX]}
  TARGET_PORT=8000
  [[ "$SERVICE" == "frontend" ]] && TARGET_PORT=8501

  log "→ $SERVICE : http://localhost:$LOCAL_PORT"
  kubectl port-forward svc/$SERVICE $LOCAL_PORT:$TARGET_PORT > /dev/null 2>&1 &
  ((INDEX++))
done

success "🎉 Tous les port-forwards sont actifs !"

echo -e "\n${YELLOW}🌐 Accès local aux services :${RESET}"
echo -e "${GREEN}http://localhost:8000/users/${RESET}        (user-service)"
echo -e "${GREEN}http://localhost:8001/movies/${RESET}       (movie-service)"
echo -e "${GREEN}http://localhost:8002/ratings/${RESET}      (rating-service)"
echo -e "${GREEN}http://localhost:8501${RESET}               (frontend Streamlit)"

# Port-forward bloquant pour frontend
kubectl port-forward svc/frontend 8501:8501

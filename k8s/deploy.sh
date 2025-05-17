#!/bin/bash

set -e

log() { echo "▶ $1"; }
success() { echo "✔ $1"; }
warn() { echo "⚠ $1"; }
error() { echo "✖ $1"; }

log "🧹 Suppression de l'ancien cluster Minikube (minikube delete)..."
minikube delete

NAMESPACE="default"
SERVICES_DIR="."

PORTS=(8000 8001 8002 8003 8501)
SERVICES=("postgres" "user-service" "movie-service" "rating-service" "frontend")

wait_for_pod_ready() {
  local label=$1
  local max_attempts=60  # temps d'attente plus long (2 minutes)
  log "⏳ Attente que le pod app=$label soit en état Running et Ready..."

  for i in $(seq 1 $max_attempts); do
    POD_NAME=$(kubectl get pods -l app=$label -o jsonpath="{.items[0].metadata.name}" 2>/dev/null || echo "")
    POD_STATUS=$(kubectl get pod "$POD_NAME" -o jsonpath="{.status.phase}" 2>/dev/null || echo "")
    CONDITION=$(kubectl get pod "$POD_NAME" -o jsonpath="{.status.conditions[?(@.type=='Ready')].status}" 2>/dev/null || echo "")

    if [[ "$POD_STATUS" == "Running" && "$CONDITION" == "True" ]]; then
      success "$label est prêt."

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

  error "$label n'est pas prêt après $((max_attempts*2))s."
  exit 1
}

log "🚀 Lancement de Minikube..."
minikube start  # décommenter si nécessaire

CLUSTER_IP=$(minikube ip)

log "📦 Déploiement de Postgres..."
kubectl apply -f "$SERVICES_DIR/postgres/deployment.yaml"
kubectl apply -f "$SERVICES_DIR/postgres/service.yaml"

wait_for_pod_ready "postgres"

for SERVICE in "${SERVICES[@]:1}"; do
  log "📦 Déploiement de $SERVICE..."
  kubectl apply -f "$SERVICES_DIR/$SERVICE/deployment.yaml"
  kubectl apply -f "$SERVICES_DIR/$SERVICE/service.yaml"
done

for SERVICE in "${SERVICES[@]:1}"; do
  # Si frontend, attente plus longue (3 minutes)
  if [[ "$SERVICE" == "frontend" ]]; then
    max_frontend_attempts=90
    log "⏳ Attente longue pour le frontend..."

    for i in $(seq 1 $max_frontend_attempts); do
      POD_NAME=$(kubectl get pods -l app=$SERVICE -o jsonpath="{.items[0].metadata.name}" 2>/dev/null || echo "")
      POD_STATUS=$(kubectl get pod "$POD_NAME" -o jsonpath="{.status.phase}" 2>/dev/null || echo "")
      CONDITION=$(kubectl get pod "$POD_NAME" -o jsonpath="{.status.conditions[?(@.type=='Ready')].status}" 2>/dev/null || echo "")

      if [[ "$POD_STATUS" == "Running" && "$CONDITION" == "True" ]]; then
        success "$SERVICE est prêt."
        break
      fi

      sleep 2
      warn "$SERVICE non prêt... tentative $i"
    done

    if [[ ! "$POD_STATUS" == "Running" || ! "$CONDITION" == "True" ]]; then
      error "$SERVICE n'est pas prêt après $((max_frontend_attempts*2))s."
      exit 1
    fi
  else
    wait_for_pod_ready "$SERVICE"
  fi
done

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

echo
echo "🌐 Accès local aux services :"
echo "http://localhost:8000/users/        (user-service)"
echo "http://localhost:8001/movies/       (movie-service)"
echo "http://localhost:8002/ratings/      (rating-service)"
echo "http://localhost:8501               (frontend Streamlit)"


# Port-forward bloquant pour frontend
kubectl port-forward svc/frontend 8501:8501
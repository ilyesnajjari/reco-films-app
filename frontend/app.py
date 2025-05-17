import streamlit as st
import requests
import os
import re

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")
MOVIE_SERVICE_URL = os.getenv("MOVIE_SERVICE_URL", "http://movie-service:8000")
RATING_SERVICE_URL = os.getenv("RATING_SERVICE_URL", "http://rating-service:8000")

st.title("🎬 Application de Films Distribuée")

# Init session state
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

def load_movies():
    try:
        res = requests.get(f"{MOVIE_SERVICE_URL}/movies/")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"Erreur de connexion au movie-service : {e}")
        return []

# ---------- AUTH ----------
if not st.session_state.user_authenticated:
    st.header("🔐 Connexion ou création d'un compte")

    with st.form("auth_form"):
        username = st.text_input("Nom d'utilisateur")
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        auth_action = st.radio("Action", ["Se connecter", "Créer un compte"])
        submitted = st.form_submit_button("Valider")

        if submitted:
            if not username or not email or not password:
                st.error("Tous les champs sont obligatoires.")
            elif not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
                st.error("❌ Adresse email invalide.")
            else:
                payload = {
                    "username": username,
                    "email": email,
                    "password": password
                }
                try:
                    if auth_action == "Créer un compte":
                        res = requests.post(f"{USER_SERVICE_URL}/users/", json=payload)
                        if res.status_code in [200, 201]:
                            st.success("✅ Compte créé avec succès.")
                            st.session_state.user_authenticated = True
                            st.session_state.current_user = res.json()
                        else:
                            st.error(f"Erreur : {res.status_code} - {res.text}")

                    elif auth_action == "Se connecter":
                        res = requests.get(f"{USER_SERVICE_URL}/users/")
                        users = res.json()
                        match = next((u for u in users if u["username"] == username and u["email"] == email), None)
                        if match:
                            st.success("✅ Connexion réussie.")
                            st.session_state.user_authenticated = True
                            st.session_state.current_user = match
                        else:
                            st.error("❌ Nom d'utilisateur ou email incorrect.")
                except Exception as e:
                    st.error(f"Erreur de connexion : {e}")
    st.stop()

# ---------- INTERFACE PRINCIPALE ----------
user = st.session_state.current_user
st.success(f"Connecté en tant que : **{user['username']}** ({user['email']})")

# ---------- SUPPRIMER MON COMPTE ----------
st.subheader("🗑️ Supprimer mon compte")

if st.button("❌ Supprimer mon compte définitivement"):
    try:
        res = requests.delete(f"{USER_SERVICE_URL}/users/{user['id']}")
        if res.status_code == 200:
            st.success("✅ Compte supprimé. Déconnexion en cours...")
            st.session_state.user_authenticated = False
            st.session_state.current_user = None
        else:
            st.error(f"Erreur de suppression : {res.status_code}")
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")

# Simple solution : 
# Pour "forcer" un rerun tu peux rajouter un bouton invisible qui remet l'app à zéro :

if not st.session_state.user_authenticated:
    st.button("Recharger la page", on_click=lambda: None)  # ça force un rerun et recharge l'interface

# ---------- TABS ----------
tab1, tab2, tab3 = st.tabs(["👤 Profil", "🎥 Films", "⭐ Notes"])

# ---------- PROFIL ----------
with tab1:
    st.subheader("👤 Mon profil")
    st.write(f"**Nom d'utilisateur :** {user['username']}")
    st.write(f"**Email :** {user['email']}")
    st.write(f"**ID :** {user['id']}")

# ---------- FILMS ----------
with tab2:
    st.header("🎥 Liste des films")
    if st.button("🔄 Charger les films"):
        movies = load_movies()
        if movies:
            for m in movies:
                st.markdown(f"**{m['title']}** - 🎬 Réalisateur : {m.get('director', 'N/A')}  \n⭐ Moyenne : `{m.get('average_rating', 'N/A')}`")
        else:
            st.info("Aucun film trouvé.")

# ---------- NOTES ----------
with tab3:
    st.subheader("⭐ Ajouter une note")

    movies = load_movies()
    movie_titles = [m['title'] for m in movies]
    movie_title_selected = st.selectbox("Sélectionner un film", options=movie_titles)

    movie_id = next((m['id'] for m in movies if m['title'] == movie_title_selected), None)

    rating = st.slider("Note", min_value=0.0, max_value=5.0, step=0.5)

    if st.button("💾 Enregistrer la note"):
        if movie_id is None:
            st.error("❌ Film non trouvé.")
        else:
            try:
                payload = {
                    "user_id": user["id"],
                    "movie_id": movie_id,
                    "rating": rating
                }
                res = requests.post(f"{RATING_SERVICE_URL}/ratings/", json=payload)
                if res.status_code in [200, 201]:
                    st.success("✅ Note enregistrée.")
                else:
                    st.error(f"❌ Erreur : {res.status_code} - {res.text}")
            except Exception as e:
                st.error(f"Erreur : {e}")

    st.markdown("---")
    st.subheader("🕘 Historique de mes notes")

    try:
        res = requests.get(f"{RATING_SERVICE_URL}/ratings/?user_id={user['id']}")
        res.raise_for_status()
        ratings = res.json()
        if not ratings:
            st.info("Aucune note enregistrée.")
        else:
            for r in ratings:
                movie_name = next((m['title'] for m in movies if m['id'] == r['movie_id']), "Film inconnu")
                st.write(f"🎬 **{movie_name}** - Note : {r['rating']} (ID note: {r['id']})")
                if st.button(f"🗑️ Supprimer la note {r['id']}", key=f"del_{r['id']}"):
                    try:
                        del_res = requests.delete(f"{RATING_SERVICE_URL}/ratings/{r['id']}")
                        if del_res.status_code == 200:
                            st.success("✅ Note supprimée.")
                        else:
                            st.error(f"Erreur suppression : {del_res.status_code}")
                    except Exception as e:
                        st.error(f"Erreur suppression : {e}")
    except Exception as e:
        st.error(f"Erreur chargement notes : {e}")

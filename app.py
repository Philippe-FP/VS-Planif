import streamlit as st
import pandas as pd
from openai import OpenAI
import io
st.write(f"Version OpenAI installée : {openai.__version__}")

# --- Titre principal ---
st.title("Assistant de planification VS – version API fichiers")

# --- Initialisation du client OpenAI ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- Sélecteur de modèle ---
st.subheader("Choisissez le modèle OpenAI")
model_choice = st.selectbox(
    "Modèle utilisé :",
    [
        "gpt-5-chat-latest",
        "gpt-5-pro",
        "gpt-5-mini",
        "gpt-5-nano",
        "gpt-4-turbo",
        "gpt-4o-mini",
    ],
    index=0,
)

st.divider()

# --- Étape 1 : Upload des fichiers CSV nécessaires ---
st.subheader("Fichiers d'entrée requis pour la planification")

uploaded_files = st.file_uploader(
    "Téléversez ici les 5 fichiers CSV nécessaires :",
    type=["csv"],
    accept_multiple_files=True
)

required_files = {
    "of_cdt.csv",
    "capacites_machine_jour.csv",
    "operateurs_disponibilites.csv",
    "operateurs_competences.csv",
    "kits_pairs - of_cdt.csv"
}

# Dictionnaire pour stocker les file_id OpenAI
file_ids = {}

if uploaded_files:
    uploaded_names = {f.name for f in uploaded_files}
    missing = required_files - uploaded_names
    extra = uploaded_names - required_files

    if missing:
        st.warning(f"Fichiers manquants : {', '.join(missing)}")
    if extra:
        st.info(f"Fichiers inattendus : {', '.join(extra)}")

    if not missing:
        st.success("Tous les fichiers requis ont été téléversés.")
        for file in uploaded_files:
            try:
                # Lecture et aperçu
                df = pd.read_csv(file)
                st.write(f"{file.name} — {df.shape[0]} lignes, {df.shape[1]} colonnes")
                st.dataframe(df.head(3))

                # Conversion en mémoire binaire (BytesIO)
                file.seek(0)
                file_bytes = io.BytesIO(file.read())

                # Upload vers OpenAI
                uploaded = client.files.create(file=file_bytes, purpose="assistants")
                file_ids[file.name] = uploaded.id
                st.caption(f"Fichier {file.name} chargé dans OpenAI (id: {uploaded.id})")

            except Exception as e:
                st.error(f"Erreur lors de la lecture ou de l'upload de {file.name} : {e}")
else:
    st.info("Glissez-déposez les 5 fichiers CSV ci-dessus pour commencer.")

st.divider()

# --- Initialisation de la mémoire conversationnelle ---
if "conversation" not in st.session_state:
    st.session_state["conversation"] = [
        {
            "role": "system",
            "content": (
                "Tu es l'assistant planificateur de production de VitalScientific. "
                "Tu disposes des fichiers CSV uploadés via l'API OpenAI et tu dois t’en servir "
                "pour générer et expliquer le planning de production (planning.csv, alertes.csv, Gantt). "
                "Tu justifies toujours tes choix de planification de manière claire et professionnelle."
            )
        }
    ]

st.subheader("💬 Discussion explicative sur le planning")

# --- Affichage de l’historique du chat ---
for msg in st.session_state["conversation"]:
    if msg["role"] == "user":
        st.markdown(f"**👤 Utilisateur :** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"**🤖 Assistant :** {msg['content']}")

# --- Zone de saisie utilisateur ---
user_input = st.text_area(
    "Posez une question ou donnez une instruction à l'assistant :",
    placeholder="Exemple : Génère le planning de la semaine 35 à partir des fichiers fournis."
)

col1, col2 = st.columns(2)
with col1:
    send_btn = st.button("Envoyer la requête")
with col2:
    reset_btn = st.button("Réinitialiser la discussion")

# --- Réinitialisation ---
if reset_btn:
    st.session_state["conversation"] = st.session_state["conversation"][:1]
    st.experimental_rerun()

# --- Envoi de la requête ---
if send_btn and user_input.strip():
    if not file_ids:
        st.warning("Veuillez d'abord téléverser les fichiers CSV nécessaires.")
    else:
        st.session_state["conversation"].append({"role": "user", "content": user_input})
        with st.spinner(f"Le modèle {model_choice} réfléchit..."):
            try:
                response = client.chat.completions.create(
                    model=model_choice,
                    messages=st.session_state["conversation"],
                    file_ids=list(file_ids.values())
                )
                answer = response.choices[0].message.content
                st.session_state["conversation"].append({"role": "assistant", "content": answer})
                st.success(answer)
            except Exception as e:
                st.error(f"Erreur lors de la requête : {e}")

st.caption("💡 Les fichiers sont transmis via l'API OpenAI et la discussion reste mémorisée tant que la session est ouverte.")

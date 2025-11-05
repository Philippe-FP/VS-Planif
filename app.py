# ================================
#  Assistant Planification VS – GPT-5
#  Version B : API Assistants (fichiers complets + persistance)
# ================================

# --- Imports principaux ---
import streamlit as st
import pandas as pd
import io
import json
import os
import time
from openai import OpenAI, __version__ as openai_version

# --- Initialisation du client OpenAI ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
st.write(f"✅ Version OpenAI installée : {openai_version}")

# --- Titre principal ---
st.title("Assistant de planification VS – version Assistants API")

# --- Sélecteur de modèle ---
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

# ================================
# ÉTAPE 1 – Upload des fichiers CSV
# ================================
st.subheader("📂 Fichiers d'entrée requis pour la planification")

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
        st.success("✅ Tous les fichiers requis ont été téléversés et vont être transmis à OpenAI.")
        for file in uploaded_files:
            try:
                df = pd.read_csv(file)
                st.write(f"**{file.name}** — {df.shape[0]} lignes × {df.shape[1]} colonnes")
                st.dataframe(df.head(3))

                # Upload complet vers OpenAI (purpose="assistants")
                file.seek(0)
                file_bytes = io.BytesIO(file.read())
                uploaded = client.files.create(file=file_bytes, purpose="assistants")
                file_ids[file.name] = uploaded.id
                st.caption(f"📤 Fichier {file.name} chargé (id: {uploaded.id})")
            except Exception as e:
                st.error(f"Erreur lors du traitement de {file.name} : {e}")
else:
    st.info("Glissez-déposez les 5 fichiers CSV ci-dessus pour commencer.")

st.divider()

# ================================
# ÉTAPE 2 – Mémoire conversationnelle locale
# ================================
if "conversation" not in st.session_state:
    st.session_state["conversation"] = [
        {
            "role": "system",
            "content": (
                "Tu es l'assistant planificateur de production de VitalScientific. "
                "Tu disposes des fichiers CSV uploadés et tu les utilises pour générer, "
                "expliquer et justifier un planning de production complet. "
                "Tu raisonnes comme un expert industriel, clair et professionnel."
            ),
        }
    ]

MEMORY_FILE = "conversation_memory.json"

def save_memory():
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state["conversation"], f, ensure_ascii=False, indent=2)
        st.toast("💾 Mémoire sauvegardée.")
    except Exception as e:
        st.error(f"Erreur sauvegarde mémoire : {e}")

def load_memory():
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                st.session_state["conversation"] = json.load(f)
            st.toast("🔁 Mémoire rechargée.")
    except Exception as e:
        st.error(f"Erreur chargement mémoire : {e}")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("💾 Sauvegarder la mémoire"):
        save_memory()
with col2:
    if st.button("🔁 Recharger la mémoire"):
        load_memory()
with col3:
    if st.button("🗑️ Réinitialiser la mémoire"):
        st.session_state["conversation"] = st.session_state["conversation"][:1]
        st.experimental_rerun()

st.divider()

# ================================
# ÉTAPE 3 – Génération du planning (Assistants API)
# ================================
st.subheader("🧮 Génération du planning")

instruction = st.text_area(
    "Consigne à l'assistant :",
    placeholder="Exemple : Génère le planning de la semaine 35 à partir des fichiers fournis."
)

if st.button("🚀 Générer le planning"):
    if not uploaded_files:
        st.warning("Veuillez d'abord téléverser les fichiers CSV nécessaires.")
    elif not instruction.strip():
        st.warning("Veuillez saisir une instruction de planification.")
    else:
        # --- Nouvelle logique : API Assistants ---
        try:
            # 1️⃣ Créer l'assistant (une seule fois)
            if "assistant_id" not in st.session_state:
                with st.spinner("Initialisation de l'assistant de planification..."):
                    assistant = client.beta.assistants.create(
                        name="Assistant Planification VS",
                        instructions=(
                            "Tu es l'assistant planificateur de production de VitalScientific. "
                            "Tu planifies à partir des CSV fournis (of_cdt, capacités, opérateurs...) "
                            "en appliquant les règles du prompt V9.1. "
                            "Tu expliques clairement tes choix et génères un résumé structuré."
                        ),
                        model=model_choice,
                        tools=[{"type": "code_interpreter"}]
                    )
                    st.session_state["assistant_id"] = assistant.id
                    st.toast("🧠 Assistant créé")

            # 2️⃣ Créer un thread (mémoire utilisateur)
            if "thread_id" not in st.session_state:
                thread = client.beta.threads.create()
                st.session_state["thread_id"] = thread.id

            # 3️⃣ Ajouter le message utilisateur dans le thread
            client.beta.threads.messages.create(
                thread_id=st.session_state["thread_id"],
                role="user",
                content=instruction,
                file_ids=list(file_ids.values()) if file_ids else None
            )

            # 4️⃣ Lancer le run
            with st.spinner("Le modèle GPT-5 exécute la planification..."):
                run = client.beta.threads.runs.create(
                    thread_id=st.session_state["thread_id"],
                    assistant_id=st.session_state["assistant_id"]
                )

                # Attente de fin d'exécution
                while True:
                    run = client.beta.threads.runs.retrieve(
                        thread_id=st.session_state["thread_id"],
                        run_id=run.id
                    )
                    if run.status == "completed":
                        break
                    elif run.status in ["failed", "cancelled", "expired"]:
                        st.error(f"Échec du run ({run.status})")
                        break
                    time.sleep(2)

            # 5️⃣ Récupérer et afficher la réponse
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state["thread_id"]
            )
            for m in messages.data:
                if m.role == "assistant":
                    for content in m.content:
                        if content.type == "text":
                            st.markdown(content.text.value)

        except Exception as e:
            st.error(f"Erreur lors du run de l'assistant : {e}")

st.divider()

# ================================
# ÉTAPE 4 – Discussion explicative (même thread)
# ================================
st.subheader("💬 Discussion explicative sur le planning")

user_question = st.text_area(
    "Posez votre question sur le planning généré :",
    placeholder="Exemple : Pourquoi l’OF 22 est-il planifié vendredi matin ?"
)

if st.button("Envoyer ma question"):
    if not user_question.strip():
        st.warning("Veuillez saisir une question.")
    else:
        try:
            # Ajouter la question dans le même thread
            client.beta.threads.messages.create(
                thread_id=st.session_state["thread_id"],
                role="user",
                content=user_question
            )

            with st.spinner("L'assistant prépare sa réponse..."):
                run = client.beta.threads.runs.create(
                    thread_id=st.session_state["thread_id"],
                    assistant_id=st.session_state["assistant_id"]
                )

                # Attente de fin
                while True:
                    run = client.beta.threads.runs.retrieve(
                        thread_id=st.session_state["thread_id"],
                        run_id=run.id
                    )
                    if run.status == "completed":
                        break
                    elif run.status in ["failed", "cancelled", "expired"]:
                        st.error(f"Échec du run ({run.status})")
                        break
                    time.sleep(2)

            # Affichage de la réponse
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state["thread_id"]
            )
            for m in messages.data:
                if m.role == "assistant":
                    for content in m.content:
                        if content.type == "text":
                            st.markdown(content.text.value)

        except Exception as e:
            st.error(f"Erreur lors de la requête : {e}")

st.caption(
    "💡 Les CSV sont transmis via l'API Assistants. "
    "Le même thread conserve la mémoire de la session, "
    "permettant des échanges explicatifs persistants comme dans ChatGPT."
)

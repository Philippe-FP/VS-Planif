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

def load

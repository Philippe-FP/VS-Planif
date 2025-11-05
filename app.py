# ================================
#  Assistant Planification VS – GPT-5
#  Streamlit + API OpenAI + Persistance
# ================================

# --- Imports principaux ---
import streamlit as st
import pandas as pd
import io
import json
import os
from openai import OpenAI, __version__ as openai_version

# --- Initialisation du client OpenAI ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- Informations techniques ---
st.write(f"✅ Version OpenAI installée : {openai_version}")

# --- Titre principal ---
st.title("Assistant de planification VS – version API fichiers")

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

                # Conversion binaire + upload vers OpenAI
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
# ÉTAPE 2 – Initialisation mémoire / contexte
# ================================
if "conversation" not in st.session_state:
    st.session_state["conversation"] = [
        {
            "role": "system",
            "content": (
                "Tu es l'assistant planificateur de production de VitalScientific. "
                "Tu disposes des fichiers CSV chargés (of_cdt, capacités, opérateurs...) "
                "et tu t'en sers pour générer, expliquer et justifier le planning "
                "de production (planning.csv, alertes.csv, Gantt). "
                "Tu raisonnes toujours comme un expert industriel, clair et professionnel."
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

# --- Contrôles mémoire ---
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

# ================================
# ÉTAPE 3 – Génération du planning
# ================================
st.subheader("🧮 Génération du planning de production")

instruction = st.text_area(
    "Consigne à l'assistant :",
    placeholder="Exemple : Génère le planning de la semaine 35 à partir des fichiers fournis."
)

if st.button("🚀 Générer le planning"):
    if not file_ids:
        st.warning("Veuillez d'abord téléverser les fichiers CSV nécessaires.")
    elif not instruction.strip():
        st.warning("Veuillez saisir une instruction de planification.")
    else:
        st.session_state["conversation"].append({"role": "user", "content": instruction})
        with st.spinner(f"Le modèle {model_choice} réfléchit..."):
            try:
                response = client.chat.completions.create(
                    model=model_choice,
                    messages=st.session_state["conversation"],
                    file_ids=list(file_ids.values())
                )
                answer = response.choices[0].message.content
                st.session_state["conversation"].append({"role": "assistant", "content": answer})
                st.success("✅ Planning généré avec succès.")
                st.markdown(answer)
            except Exception as e:
                st.error(f"Erreur lors de la requête : {e}")

st.divider()

# ================================
# ÉTAPE 4 – Discussion explicative persistante
# ================================
st.subheader("💬 Discussion explicative sur le planning")

for msg in st.session_state["conversation"]:
    if msg["role"] == "user":
        st.markdown(f"**👤 Utilisateur :** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"**🤖 Assistant :** {msg['content']}")

user_question = st.text_area(
    "Posez votre question sur le planning généré :",
    placeholder="Exemple : Pourquoi l’OF 22 est-il planifié vendredi matin ?"
)

if st.button("Envoyer ma question"):
    if not user_question.strip():
        st.warning("Veuillez saisir une question.")
    else:
        st.session_state["conversation"].append({"role": "user", "content": user_question})
        with st.spinner("L'assistant réfléchit..."):
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

st.caption("💡 Les fichiers sont transmis via l'API OpenAI. "
           "La discussion et la mémoire sont conservées tant que la session est ouverte "
           "et peuvent être sauvegardées/rechargées pour un usage ultérieur.")

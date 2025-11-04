import streamlit as st
import pandas as pd
from openai import OpenAI

# --- Titre principal ---
st.title("Assistant de planification VS")

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
        "gpt-5-codex",
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

# Liste des noms de fichiers attendus
required_files = {
    "of_cdt.csv",
    "capacites_machine_jour.csv",
    "operateurs_disponibilites.csv",
    "operateurs_competences.csv",
    "kits_pairs - of_cdt.csv"
}

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
                df = pd.read_csv(file)
                st.write(f"{file.name} — {df.shape[0]} lignes, {df.shape[1]} colonnes")
                st.dataframe(df.head(3))
            except Exception as e:
                st.error(f"Erreur lors de la lecture de {file.name} : {e}")
else:
    st.info("Glissez-déposez les 5 fichiers CSV ci-dessus pour commencer.")

st.divider()

# --- Test rapide du modèle (facultatif) ---
st.subheader("Test rapide du modèle OpenAI")

prompt = st.text_area(
    "Saisissez une instruction à envoyer au modèle :",
    placeholder="Ex : Dis bonjour à VitalScientific..."
)

if st.button("Envoyer au modèle"):
    if not prompt.strip():
        st.warning("Merci de saisir un message avant d’envoyer.")
    else:
        with st.spinner(f"Le modèle {model_choice} réfléchit..."):
            try:
                response = client.chat.completions.create(
                    model=model_choice,
                    messages=[{"role": "user", "content": prompt}],
                )
                message = response.choices[0].message.content
                st.success(message)
                st.caption(f"Réponse générée par le modèle : {model_choice}")
            except Exception as e:
                st.error(f"Erreur : {e}")

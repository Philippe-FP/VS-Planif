import streamlit as st
import pandas as pd
from openai import OpenAI

# --- Titre principal ---
st.title("🧠 Assistant de planification VS")

# --- Initialisation du client OpenAI (clé déjà stockée dans les secrets) ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- Sélecteur de modèle (préserve ce qu’on a fait précédemment) ---
st.subheader("⚙️ Choisissez le modèle OpenAI")
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
st.subheader("📂 Fichiers d'entrée requis pour la planification")

# Liste des fichiers attendus
required_files = [
    "of_cdt.csv",
    "capacites_machine_jour.csv",
    "operateurs_disponibilites.csv",
    "operateurs_competences.csv",
    "kits_pairs - of_cdt.csv",
]

uploaded_files = {}

for file_name in required_files:
    uploaded_files[file_name] = st.file_uploader(
        f"Téléverser {file_name}", type=["csv"], key=file_name
    )

# --- Vérification et affichage d'un résumé ---
if all(uploaded_files.values()):
    st.success("✅ Tous les fichiers ont été téléversés avec succès.")
    for name, file in uploaded_files.items():
        try:
            df = pd.read_csv(file)
            st.write(f"**{name}** — {df.shape[0]} lignes, {df.shape[1]} colonnes")
            st.dataframe(df.head(3))
        except Exception as e:
            st.error(f"Erreur lors de la lecture de {name} : {e}")
else:
    st.info("🕐 Veuillez téléverser l’ensemble des 5 fichiers avant de lancer la planification.")

st.divider()

# --- Bloc GPT simple conservé pour test du modèle ---
st.subheader("💬 Test rapide du modèle (optionnel)")
prompt = st.text_area("Saisissez une instruction pour tester GPT :", placeholder="Ex : Dis bonjour à VitalScientific…")

if st.button("🚀 Envoyer au modèle"):
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
                st.caption(f"💡 Réponse générée par le modèle : {model_choice}")
            except Exception as e:
                st.error(f"Erreur : {e}")

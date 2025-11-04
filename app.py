import streamlit as st
from openai import OpenAI

# --- Titre principal ---
st.title("🧠 Assistant de planification VS – Test OpenAI")

# --- Initialisation du client OpenAI ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- Sélecteur de modèle ---
st.subheader("⚙️ Choisissez le modèle OpenAI")
model_choice = st.selectbox(
    "Modèle utilisé :",
    [
        "gpt-5-chat-latest",   # valeur par défaut
        "gpt-5-pro",
        "gpt-5-mini",
        "gpt-5-nano",
        "gpt-5-codex",
        "gpt-4-turbo",
        "gpt-4o-mini"
    ],
    index=0  # sélection par défaut (gpt-5-chat-latest)
)

# --- Zone de saisie du prompt ---
prompt = st.text_area(
    "📝 Saisissez votre message ici :",
    placeholder="Exemple : Analyse ce planning de production ou Dis bonjour à VitalScientific..."
)

# --- Bouton d'envoi ---
if st.button("🚀 Envoyer la requête"):
    if not prompt.strip():
        st.warning("Merci de saisir un message avant d’envoyer.")
    else:
        with st.spinner(f"Le modèle {model_choice} réfléchit..."):
            try:
                response = client.chat.completions.create(
                    model=model_choice,
                    messages=[{"role": "user", "content": prompt}]
                )
                message = response.choices[0].message.content
                st.success(message)
                st.caption(f"💡 Réponse générée par le modèle : {model_choice}")
            except Exception as e:
                st.error(f"Erreur : {e}")

# --- Ligne de séparation ---
st.divider()

# --- Option : lister les modèles disponibles ---
st.subheader("🔍 Lister les modèles accessibles")
if st.button("Afficher la liste des modèles OpenAI"):
    with st.spinner("Chargement des modèles..."):
        try:
            models = client.models.list()
            model_list = [m.id for m in models.data if "gpt" in m.id.lower()]
            if model_list:
                st.write("### Modèles disponibles :")
                for m in sorted(model_list):
                    st.write(f"• {m}")
            else:
                st.warning("Aucun modèle GPT détecté pour ce compte.")
        except Exception as e:
            st.error(f"Erreur lors de la récupération des modèles : {e}")


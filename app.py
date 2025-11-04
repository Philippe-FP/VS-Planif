import streamlit as st
from openai import OpenAI

# Titre principal
st.title("Assistant de planification VS – Test OpenAI")

# Initialisation du client OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Zone de saisie et bouton principal
prompt = st.text_area("Posez une question à GPT :", "Dis bonjour à VitalScientific !")

if st.button("Envoyer"):
    with st.spinner("Réflexion en cours..."):
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        st.success(response.choices[0].message.content)

# --- Nouvelle section : Lister les modèles disponibles ---
st.divider()
st.subheader("🔍 Lister les modèles disponibles sur ce compte")

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


import streamlit as st
from openai import OpenAI
import os

st.title("Assistant de planification VS – Test OpenAI")

# Création du client OpenAI à partir de la clé stockée dans les secrets Streamlit
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Zone de saisie utilisateur
prompt = st.text_area("Posez une question à GPT-4 :", "Dis bonjour à VitalScientific !")

if st.button("Envoyer"):
    with st.spinner("Réflexion en cours..."):
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        st.success(response.choices[0].message.content)

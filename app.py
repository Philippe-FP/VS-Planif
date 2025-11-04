# --- Étape 1 : Upload des fichiers CSV nécessaires ---
st.subheader("📂 Fichiers d'entrée requis pour la planification")

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
        st.warning(f"⚠️ Fichiers manquants : {', '.join(missing)}")
    if extra:
        st.info(f"ℹ️ Fichiers inattendus : {', '.join(extra)}")

    if not missing:
        st.success("✅ Tous les fichiers requis ont été téléversés.")
        for file in uploaded_files:
            try:
                df = pd.read_csv(file)
                st.write(f"**{file.name}** — {df.shape[0]} lignes, {df.shape[1]} colonnes")
                st.dataframe(df.head(3))
            except Exception as e:
                st.error(f"Erreur lors de la lecture de {file.name} : {e}")
else:
    st.info("🕐 Glissez-déposez les 5 fichiers CSV ci-dessus pour commencer.")

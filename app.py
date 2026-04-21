import streamlit as st
import os
from dotenv import load_dotenv
from audit_engine import analyze_audit
from report_generator import generate_audit_report

load_dotenv()

# Initialisation session state
if 'pdf_file' not in st.session_state:
    st.session_state.pdf_file = None
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'constat_text' not in st.session_state:
    st.session_state.constat_text = ""

st.set_page_config(page_title="Vision-Audit 360", layout="wide", page_icon="🔍")
st.title("🔍 Vision-Audit 360")
st.markdown("**Système d’Audit Qualité Continu par Intelligence Artificielle**  \n*De la détection visuelle à l’action corrective automatisée – ISO 9001*")

st.divider()

col1, col2 = st.columns([3, 2])

with col1:
    constat_text = st.text_area(
        "📝 Saisie du constat terrain",
        height=220,
        placeholder="Décrivez précisément ce que vous observez...",
        value=st.session_state.constat_text
    )

with col2:
    uploaded_image = st.file_uploader("📸 Photo de la situation terrain", type=["jpg", "jpeg", "png"])
    if uploaded_image:
        st.image(uploaded_image, caption="Image chargée", use_container_width=True)

# Bouton principal d'analyse
if st.button("🚀 Lancer l’audit intelligent", type="primary", use_container_width=True):
    if not constat_text.strip() or not uploaded_image:
        st.error("❌ Veuillez saisir un constat ET uploader une image.")
    else:
        image_bytes = uploaded_image.read()
        
        with st.spinner("🔍 Analyse RAG en cours..."):
            result = analyze_audit(constat_text, image_bytes)

        st.success("✅ Audit terminé avec succès !")

        st.session_state.analysis_result = result
        st.session_state.constat_text = constat_text

        with st.spinner("📄 Génération du rapport PDF..."):
            pdf_file = generate_audit_report(result, constat_text)
            st.session_state.pdf_file = pdf_file

# ====================== AFFICHAGE DES RÉSULTATS ======================
if st.session_state.analysis_result:
    result = st.session_state.analysis_result

    # Ligne 1 : Score de conformité + Priorité
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("📊 Score de conformité")
        score = result.get("conformite_score", 0)
        st.progress(score / 100)
        st.metric("Score global", f"{score}%", delta=None)
    
    with col_b:
        st.subheader("⏱️ Priorité d'action")
        priorite = result.get("priorite_action", "Non défini")
        delai = result.get("delai_recommandation", "Non défini")
        couleur = result.get("priorite_couleur", "gray")
        if couleur == "red":
            st.error(f"{priorite} - Délai : {delai}")
        elif couleur == "orange":
            st.warning(f"{priorite} - Délai : {delai}")
        else:
            st.success(f"{priorite} - Délai : {delai}")

    st.divider()

    # Diagnostic
    st.subheader("📋 Diagnostic")
    st.info(result.get("diagnostic", "Non disponible"))

    # Clauses ISO
    st.subheader("📌 Clauses ISO 9001 concernées")
    clauses = result.get("clauses_concernees", [])
    if clauses:
        st.markdown(" • " + " • ".join(clauses))
    else:
        st.write("Aucune clause identifiée")

    # Niveau de risque
    st.subheader("⚠️ Niveau de risque")
    risque = result.get("niveau_risque", "Non défini")
    if "Élevé" in risque:
        st.error(f"🔴 {risque}")
    elif "Moyen" in risque:
        st.warning(f"🟠 {risque}")
    else:
        st.success(f"🟢 {risque}")

    # Actions correctives
    st.subheader("🔧 Actions correctives proposées")
    actions = result.get("actions_correctives", [])
    if actions:
        for i, act in enumerate(actions, 1):
            st.write(f"{i}. {act}")
    else:
        st.write("Aucune action corrective proposée.")

    # Recommandations
    st.subheader("💡 Recommandations supplémentaires")
    st.write(result.get("recommandations", "Aucune recommandation supplémentaire."))

    # ====================== TÉLÉCHARGEMENT PDF ======================
    if st.session_state.pdf_file and os.path.exists(st.session_state.pdf_file):
        st.divider()
        with open(st.session_state.pdf_file, "rb") as f:
            st.download_button(
                label="📄 Télécharger le rapport PDF complet",
                data=f,
                file_name=os.path.basename(st.session_state.pdf_file),
                mime="application/pdf",
                use_container_width=True
            )
        st.success(f"✅ Rapport généré avec succès !")

st.divider()
st.caption("Vision-Audit 360 • Prototype académique • Étape 6 : Raisonnement enrichi (score + priorité)")
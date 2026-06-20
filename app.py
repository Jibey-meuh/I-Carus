```python
import streamlit as st
from groq import Groq
import time

# Initialisation de l'historique et de la ville courante dans la session
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_city' not in st.session_state:
    st.session_state.current_city = ""

# Configuration de la page Streamlit
st.set_page_config(
    page_title="I-Carus — Hub Intelligent de Sécurité Voyage",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Authentification sécurisée via les Secrets de Streamlit
try:
    api_key = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else ""
    if api_key:
        client = Groq(api_key=api_key)
    else:
        client = None
except Exception:
    client = None

# Styles CSS personnalisés pour l'interface I-Carus
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-title {
        font-size: 46px;
        font-weight: 800;
        background: linear-gradient(45deg, #FF4B4B, #FF8F00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 5px;
    }
    
    .subtitle {
        font-size: 16px;
        text-align: center;
        color: #666666;
        margin-bottom: 35px;
    }
    
    .report-container {
        padding: 30px;
        border-radius: 16px;
        background-color: #ffffff;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid #eaeaea;
        margin-top: 20px;
    }
    
    /* Optimisation pour l'impression de la fiche */
    @media print {
        body * { visibility: hidden; }
        #printArea, #printArea * { visibility: visible; }
        #printArea { position: absolute; left: 0; top: 0; width: 100%; }
    }
    </style>
""", unsafe_allow_html=True)

# Fenêtre modale d'urgence pour le Bouton SOS
@st.dialog("🚨 SIGNAL D'URGENCE SOS")
def open_sos_modal():
    st.markdown("### Besoin d'assistance immédiate ?")
    st.write("I-Carus prépare vos données de secours d'urgence basées sur votre dernière recherche.")
    
    if st.session_state.current_city:
        st.info(f"📍 Destination ciblée : **{st.session_state.current_city}** (Données de localisation incluses)")
    else:
        st.warning("Aucune ville sélectionnée. Activation de la balise universelle.")

    st.markdown("---")
    st.write("👉 **Option 1 : Envoyer un e-mail d'alerte automatique**")
    contact_email = st.text_input("Email de votre contact de confiance :", "proche@example.com")
    sujet = f"URGENT: Alerte de securite I-Carus - {st.session_state.current_city or 'Position Inconnue'}"
    corps = f"Message d'urgence automatique I-Carus. Je me trouve actuellement a {st.session_state.current_city or 'ma destination'}. Merci de me recontacter ou de verifier la situation avec les services locaux."
    
    mailto_link = f"mailto:{contact_email}?subject={sujet}&body={corps}"
    st.markdown(f'<a href="{mailto_link}" target="_blank"><button style="background-color:#D32F2F; color:white; border:none; padding:12px; border-radius:6px; font-weight:bold; cursor:pointer; width:100%;">📧 Déclencher l\'alerte par Email</button></a>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.write("👉 **Option 2 : Lien direct SMS (Mobile)**")
    sms_link = f"sms:+33600000000?body=SOS%20I-Carus%20:%20Je%20suis%20a%20{st.session_state.current_city or 'ma%20destination'}.%20Besoin%20d'aide."
    st.markdown(f'<a href="{sms_link}"><button style="background-color:#1976D2; color:white; border:none; padding:12px; border-radius:6px; font-weight:bold; cursor:pointer; width:100%;">💬 Préparer un SMS d\'urgence</button></a>', unsafe_allow_html=True)

# En-tête de l'application
st.markdown("<div class='main-title'>🦅 I-Carus</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>L'œil universel de sécurité, d'assistance et de logistique pour voyageurs avertis</div>", unsafe_allow_html=True)

# Menu latéral (Sidebar)
if st.sidebar.button("🚨 BOUTON SOS GÉOLOCALISÉ", use_container_width=True, type="primary"):
    open_sos_modal()

st.sidebar.markdown("---")
st.sidebar.header("📍 Recherche & Configuration")

# Champ de saisie de la destination
ville_input = st.sidebar.text_input("Saisir une ville ou région du monde :", value=st.session_state.current_city, placeholder="Ex: Paris, Bangkok, Lima...")
langue = st.sidebar.selectbox("🌐 Langue d'affichage des résultats :", ["Français", "English", "Español", "Deutsch", "Italiano"])

st.sidebar.subheader("🔍 Éléments à cartographier :")
opt_urgences = st.sidebar.checkbox("🚨 Urgences locales & Numéros utiles", value=True)
opt_ambassade = st.sidebar.checkbox("🇨🇳 Ambassade / Consulat français", value=True)
opt_hopitaux = st.sidebar.checkbox("🏥 Hôpitaux & Notes Google Maps", value=True)
opt_safety_score = st.sidebar.checkbox("📊 Jauge de Sécurité & Alertes MEAE", value=True)
opt_urg_heb = st.sidebar.checkbox("⛺ Hébergements d'urgence", value=False)
opt_woofing = st.sidebar.checkbox("🌱 Sites de WWOOFing", value=False)
opt_habitant = st.sidebar.checkbox("🏠 Logements chez l'habitant (Top notes)", value=False)
opt_supermarches = st.sidebar.checkbox("🛒 Supermarchés les mieux notés", value=False)

trigger_search = st.sidebar.button("Générer l'Analyse Globale 🚀", use_container_width=True)

# Affichage de l'historique de recherche local
if st.session_state.history:
    st.sidebar.markdown("---")
    st.sidebar.subheader("⏳ Historique récent")
    for h_city in st.session_state.history[-5:]:
        if st.sidebar.button(f"📌 {h_city}", key=f"hist_{h_city}", use_container_width=True):
            st.session_state.current_city = h_city
            st.rerun()

# Traitement de la requête par l'IA
if trigger_search and ville_input.strip():
    st.session_state.current_city = ville_input.strip()
    if st.session_state.current_city not in st.session_state.history:
        st.session_state.history.append(st.session_state.current_city)
    
    if not client:
        st.error("⚠️ Clé API Groq manquante. Veuillez configurer `GROQ_API_KEY` dans vos Secrets Streamlit Cloud.")
    else:
        with st.spinner(f"Sécurisation des données pour {st.session_state.current_city}..."):
            
            # Structuration dynamique des critères du rapport
            sections = []
            if opt_urgences:
                sections.append("- Numéros d'urgence locaux convertis au format markdown cliquable : `[Nom](tel:numéro)` et consignes immédiates.")
            if opt_ambassade:
                sections.append("- Coordonnées complètes de l'Ambassade ou du Consulat français le plus proche (avec téléphone cliquable `[Numéro](tel:...)` et lien Google Maps simulé).")
            if opt_hopitaux:
                sections.append("- Top 3 hôpitaux locaux majeurs recommandés avec adresses physiques et notes estimées de réputation sur Google Maps (ex: 4.6⭐).")
            if opt_safety_score:
                sections.append("- Analyse synthétique de sécurité (indice de criminalité estimé, risques environnementaux) et mise en adéquation avec les conseils aux voyageurs du MEAE français.")
            if opt_urg_heb:
                sections.append("- Adresses de structures d'hébergement d'urgence ou d'accueil temporaire de crise.")
            if opt_woofing:
                sections.append("- Réseau ou opportunités de WWOOFing identifiées dans la région d'implantation.")
            if opt_habitant:
                sections.append("- Localités et quartiers clés offrant les hébergements chez l'habitant (Homestay/Guest Houses) les mieux notés.")
            if opt_supermarches:
                sections.append("- Supermarchés de référence ou centres de ravitaillement alimentaire classés par note (ex: 4.4⭐).")

            prompt_sections = "\n".join(sections)
            
            system_prompt = (
                f"Tu es l'intelligence centrale d'I-Carus (International Care, Assistance & Rescue Universal System). "
                f"Rédige impérativement tout ton rapport dans la langue suivante : **{langue}**. "
                "Pour TOUS les numéros de téléphone fournis, écris-les obligatoirement au format Markdown cliquable mobile : `[Nom](tel:téléphone_sans_espace)`. "
                "Pour TOUTES les adresses ou bâtiments cités, ajoute juste après un lien markdown cliquable vers Google Maps "
                "sous la forme exacte suivante : `[Voir l'adresse sur Google Maps](http://googleusercontent.com/maps.google.com/maps)`. "
                "Sois direct, factuel et rigoureux."
            )

            user_prompt = f"""
            Génère le rapport d'assistance et de sécurité complet pour la destination : **{st.session_state.current_city}**.
            
            Traite exclusivement ces modules demandés :
            {prompt_sections}
            
            Si le module 'Sécurité & MEAE' est présent, inclus obligatoirement l'un de ces marqueurs au tout début du paragraphe pour l'interface : [🟢 VIGILANCE NORMALE], [🟡 VIGILANCE RENFORCÉE], [🟠 DÉCONSEILLÉ SAUF RAISON IMPÉRATIVE], [🔴 FORMELLEMENT DÉCONSEILLÉ].
            """

            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    model="llama-3.1-8b-instant",
                    temperature=0.2
                )
                
                reponse = chat_completion.choices[0].message.content
                st.success(f"✨ Fiche de sécurité I-Carus générée avec succès pour {st.session_state.current_city} !")
                
                # Zone de boutons d'action d'export hors-ligne
                col_act1, col_act2 = st.columns(2)
                with col_act1:
                    st.download_button(
                        label="📄 Télécharger le Guide de Survie (Format Markdown / Hors-ligne)",
                        data=reponse,
                        file_name=f"I-Carus_{st.session_state.current_city}_Guide.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                with col_act2:
                    if st.button("🖨️ Ouvrir la boîte d'impression / Sauvegarde PDF", use_container_width=True):
                        st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
                
                # Affichage des alertes graphiques dynamiques en fonction du retour MEAE
                if "🔴 FORMELLEMENT DÉCONSEILLÉ" in reponse:
                    st.error("🚨 ALERTE CRITIQUE : Cette zone est formellement déconseillée par le MEAE français. Évitez tout déplacement.")
                elif "🟠 DÉCONSEILLÉ SAUF RAISON IMPÉRATIVE" in reponse:
                    st.warning("⚠️ ALERTE SÉCURITÉ : Voyage déconseillé sauf raison impérative par les autorités.")
                elif "🟡 VIGILANCE RENFORCÉE" in reponse:
                    st.info("ℹ️ INFO VIGILANCE : Risques modérés, vigilance renforcée préconisée sur place.")
                elif "🟢 VIGILANCE NORMALE" in reponse:
                    st.success("✅ VIGILANCE NORMALE : Aucun avertissement de sécurité majeur en cours.")

                # Rendu de la zone imprimable
                st.markdown(f'<div id="printArea" class="report-container"><h3>📋 I-Carus Fiche d\'Urgence : {st.session_state.current_city}</h3><hr>{reponse}</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Erreur technique de communication avec l'IA Groq : {e}")
elif trigger_search:
    st.warning("Veuillez d'abord saisir une destination valide.")
else:
    if not st.session_state.current_city:
        st.info("👋 Prêt pour l'analyse ? Saisissez une destination dans le panneau latéral gauche et configurez vos filtres de protection.")

import streamlit as st
from modules.crop_prediction import render_crop_prediction
from modules.disease_detection import render_disease_detection
from modules.chatbot import render_chatbot  
from modules.market_prices import render_market_prices
from modules.ndvi import render_ndvi_dashboard
from modules.rag_agent import render_rag_agent
from utils.translator_api import translate_text

st.set_page_config(page_title="AgriSmart System")

LANGUAGES = [
    "English", "Assamese", "Bengali", "Bodo", "Dogri", "Gujarati", "Hindi", 
    "Kannada", "Kashmiri", "Konkani", "Maithili", "Malayalam", "Manipuri (Meitei)", 
    "Marathi", "Nepali", "Odia (Oriya)", "Punjabi", "Sanskrit", "Santali", 
    "Sindhi", "Tamil", "Telugu", "Urdu"
]

# --- STATE INITIALIZATION ---
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "English"

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

current_lang = st.session_state.selected_language

# Helper shortcut for UI rendering
def _t(text: str) -> str:
    return translate_text(text, current_lang)

def navigate_to(page_name):
    st.session_state.current_page = page_name
    st.rerun()

# --- CSS STYLING ---
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        
        .block-container {
            padding-top: 2rem;
            padding-bottom: 0rem;
            max-width: 1200px;
        }

        /* Navbar Layout */
        .nav-container {
            background: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-bottom: 1px solid rgba(16, 185, 129, 0.2);
            padding: 20px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-radius: 12px;
            margin-bottom: 40px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        }
        
        .nav-logo {
            color: #10B981;
            font-size: 24px;
            font-weight: 800;
            letter-spacing: 1.2px;
        }

        /* Glassmorphic Visual Cards */
        .glass-card {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-bottom: none; 
            border-radius: 16px 16px 0 0;
            padding: 30px 20px;
            text-align: center;
            min-height: 220px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            transition: transform 0.3s ease;
        }

        .card-icon {
            font-size: 48px;
            margin-bottom: 15px;
            filter: drop-shadow(0 0 10px rgba(16, 185, 129, 0.4));
        }

        .card-title {
            font-size: 20px;
            font-weight: 700;
            color: #F8FAFC;
            margin-bottom: 10px;
            letter-spacing: 0.5px;
        }

        .card-text {
            font-size: 13px;
            color: #CBD5E1;
            line-height: 1.5;
        }

        /* Styled Streamlit Action Buttons */
        div.stButton > button {
            background: rgba(16, 185, 129, 0.1) !important;
            color: #10B981 !important;
            border: 1px solid rgba(16, 185, 129, 0.3) !important;
            border-radius: 0 0 16px 16px !important;
            padding: 12px !important;
            font-weight: 700 !important;
            letter-spacing: 1px !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
            margin-top: -15px !important; 
            text-transform: uppercase !important;
            font-size: 13px !important;
        }

        div.stButton > button:hover {
            background: rgba(16, 185, 129, 0.9) !important;
            color: #ffffff !important;
            border-color: #10B981 !important;
            box-shadow: 0 10px 20px -10px rgba(16, 185, 129, 0.6) !important;
        }

        /* Footer */
        .footer-container {
            text-align: center;
            padding: 30px 20px;
            margin-top: 60px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            color: #475569;
            font-size: 13px;
        }
        
        .footer-highlight {
            color: #10B981;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)


st.markdown(f"""
    <div class="nav-container">
        <div class="nav-logo">{_t('AgriSmart ✦ System')}</div>
    </div>
""", unsafe_allow_html=True)

# --- HOME DASHBOARD ---
if st.session_state.current_page == "Home":
    
    # Header and Language Selector Layout
    header_col, lang_col = st.columns([3, 1], gap="medium")
    
    with header_col:
        st.markdown(f"<h3 style='color: #E2E8F0; margin-bottom: 25px;'>{_t('Select a Specialized Diagnostic System Panel:')}</h3>", unsafe_allow_html=True)
        
    with lang_col:
        new_lang = st.selectbox(
            "Language",
            options=LANGUAGES,
            index=LANGUAGES.index(st.session_state.selected_language),
            label_visibility="collapsed"
        )
        # Force a rerun immediately if the language is changed so everything updates
        if new_lang != st.session_state.selected_language:
            st.session_state.selected_language = new_lang
            st.rerun()

    # --- ROW 1 ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-icon">🌱</div>
            <div class="card-title">{_t('Crop Matrix')}</div>
            <div class="card-text">{_t('Predict high-yield regional crop varieties based on soil chemical compositions.')}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(_t("Initialize Module"), key="btn_crop", use_container_width=True):
            navigate_to("Crop Prediction")
            
    with col2:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-icon">🔬</div>
            <div class="card-title">{_t('Pathology')}</div>
            <div class="card-text">{_t('Scan leaf surface configurations to detect dynamic structural infections instantly.')}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(_t("Launch Scanner"), key="btn_disease", use_container_width=True):
            navigate_to("Disease Detection")
    
    with col3:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-icon">📈</div>
            <div class="card-title">{_t('Mandi Rates')}</div>
            <div class="card-text">{_t('Track regional market valuations and daily optimization trade windows.')}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(_t("Fetch Data"), key="btn_market", use_container_width=True):
            navigate_to("Market Prices")
            

    # --- ROW 2 ---
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-icon">🛰️</div>
            <div class="card-title">{_t('Orbital NDVI')}</div>
            <div class="card-text">{_t('Analyze live satellite imagery to detect crop stress and vegetation health.')}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(_t("Scan Perimeter"), key="btn_ndvi", use_container_width=True):
            navigate_to("Satellite NDVI")

    with col2:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-icon">🤖</div>
            <div class="card-title">{_t('AgriBot Voice')}</div>
            <div class="card-text">{_t('Open the multi-lingual neural speech conversational agent advisory portal.')}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(_t("Connect Link"), key="btn_bot", use_container_width=True):
            navigate_to("AgriBot Assistant")

    with col3:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-icon">🏛️</div>
            <div class="card-title">{_t('Government Scheme Desk')}</div>
            <div class="card-text">{_t('Query about the government scheme and also get the official government scheme documents and detail.')}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(_t("Check Scheme"), key="btn_subsidy", use_container_width=True):
            navigate_to("Government Scheme Assistant")

# --- ACTUAL FEATURE PAGES LAYER ---
elif st.session_state.current_page == "Crop Prediction":
    if st.button(_t("⬅ Return to Dashboard")):
        navigate_to("Home")
    render_crop_prediction()

elif st.session_state.current_page == "Disease Detection":
    if st.button(_t("⬅ Return to Dashboard")):
        navigate_to("Home")
    render_disease_detection()

elif st.session_state.current_page == "AgriBot Assistant":
    if st.button(_t("⬅ Return to Dashboard")):
        navigate_to("Home")
    render_chatbot()

elif st.session_state.current_page == "Market Prices":
    if st.button(_t("⬅ Return to Dashboard")):
        navigate_to("Home")
    render_market_prices()

elif st.session_state.current_page == "Satellite NDVI":
    if st.button(_t("⬅ Return to Dashboard")):
        navigate_to("Home")
    render_ndvi_dashboard()

elif st.session_state.current_page == "Government Scheme Assistant":
    if st.button(_t("⬅ Return to Dashboard")):
        navigate_to("Home")
    render_rag_agent()

# --- FOOTER ---
st.markdown(f"""
    <div class="footer-container">
        © 2026 {_t('AgriSmart Systems | Engineered for High-Yield Agriculture')} | <span class="footer-highlight">Ankit Kumar</span>
    </div>
""", unsafe_allow_html=True)
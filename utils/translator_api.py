import streamlit as st
from deep_translator import GoogleTranslator

# Map full names to Google Translate ISO language codes for all 22 Official Indian Languages + English
LANG_CODES = {
    "English": "en",
    "Assamese": "as",
    "Bengali": "bn",
    "Bodo": "brx",
    "Dogri": "doi",
    "Gujarati": "gu",
    "Hindi": "hi",
    "Kannada": "kn",
    "Kashmiri": "ks",
    "Konkani": "gom",
    "Maithili": "mai",
    "Malayalam": "ml",
    "Manipuri (Meitei)": "mni-Mtei",
    "Marathi": "mr",
    "Nepali": "ne",
    "Odia (Oriya)": "or",
    "Punjabi": "pa",
    "Sanskrit": "sa",
    "Santali": "sat",
    "Sindhi": "sd",
    "Tamil": "ta",
    "Telugu": "te",
    "Urdu": "ur"
}

@st.cache_data(show_spinner=False)
def translate_text(text: str, target_lang: str) -> str:
    """
    Translates text dynamically using Google's translation backend via deep-translator.
    """
    target_code = LANG_CODES.get(target_lang, "en")
    
    if target_code == "en" or not text.strip():
        return text

    try:
        translator = GoogleTranslator(source='auto', target=target_code)
        return translator.translate(text)
    except Exception:
        return text
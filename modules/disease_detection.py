import streamlit as st
from PIL import Image
from utils.api import identify_plant_disease_api, analyze_disease_with_llm
from utils.translator_api import translate_text

def render_disease_detection():
    # Fetch the dynamically selected language from the session state
    current_lang = st.session_state.get("selected_language", "English")
    
    # Internal helper to translate strings in this module
    def _t(text: str) -> str:
        return translate_text(text, current_lang)

    st.header(f"🍂 {_t('Cloud Vision Leaf Diagnostic Panel')}")
    st.write(_t("Upload a photographic leaf sample. The image will be processed via the Plant.id global botanical database."))
    
    uploaded_file = st.file_uploader(_t("Upload leaf specimen graphic..."), type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        # Display the uploaded image
        img = Image.open(uploaded_file).convert('RGB')
        
        # Displaying the image (using use_container_width for responsive layout)
        st.image(img, caption=_t("Target Specimen Image Matrix"), width='stretch')
        
        if st.button(_t("Run Cloud Diagnostic Engine"), type="primary"):
            with st.spinner(_t("Transmitting image telemetry to Plant.id API servers...")):
                
                # Extract raw bytes from the uploaded file
                image_bytes = uploaded_file.getvalue()
                
                # Call the Plant.id API
                detected_disease = identify_plant_disease_api(image_bytes)
                
                # Handle Errors
                if "Error" in detected_disease or "Failed" in detected_disease:
                    st.error(_t(detected_disease))
                    return
                
                # Note: We check against the exact English API response before translating
                if detected_disease == "Healthy Plant":
                    st.success(_t("Analysis complete! No pathogenic elements is found. The plant appears healthy."))
                    return
                
                st.error(_t("Analysis complete! Pathogenic infection elements is found."))
                st.warning(f"**{_t('Diagnostic Disease Class')} : {_t(detected_disease)}**")
                
                # Pass the detected disease name to OpenAI for dynamic treatment protocol
                st.subheader(f"🛡️ {_t('Dynamic Medical & Treatment Protocol')}")
                with st.spinner(_t("Generating specialized treatment protocol via OpenAI...")):
                    treatment_report = analyze_disease_with_llm(detected_disease)
                    # Translate the entire generated medical report into the selected language
                    st.write(_t(treatment_report))
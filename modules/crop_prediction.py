import streamlit as st
import numpy as np
from utils.api import fetch_automated_environmental_data, generate_crop_financials
from utils.models import load_crop_classifier
from utils.translator_api import translate_text

CROP_DICT = {
    1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut", 6: "Papaya", 7: "Orange",
    8: "Apple", 9: "Muskmelon", 10: "Watermelon", 11: "Grapes", 12: "Mango", 13: "Banana",
    14: "Pomegranate", 15: "Lentil", 16: "Blackgram", 17: "Mungbean", 18: "Mothbeans",
    19: "Pigeonpeas", 20: "Kidneybeans", 21: "Chickpea", 22: "Coffee"
}

def render_crop_prediction():
    # Fetch the dynamically selected language from the session state
    current_lang = st.session_state.get("selected_language", "English")
    
    # Internal helper to translate strings in this module
    def _t(text: str) -> str:
        return translate_text(text, current_lang)

    st.header(f"🌾 {_t('Automated Crop & Economic Predictor')}")
    st.write(_t("Zero manual entry required for soil or weather data. Enter your GPS coordinates to query remote sensing telemetry networks."))
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"📍 {_t('Target Coordinates')}")
        # Replaced the single text input with precise Lat/Lon numerical inputs
        c_lat, c_lon = st.columns(2)
        with c_lat:
            lat_input = st.number_input(_t("Latitude"), value=25.6154, format="%.6f")
        with c_lon:
            lon_input = st.number_input(_t("Longitude"), value=85.1010, format="%.6f")
            
    with col2:
        st.subheader(f"📐 {_t('Farm scale')}")
        land_size = st.number_input(_t("Total Land Size (Acres)"), min_value=0.1, value=5.0)
        previous_yield = st.text_input(_t("Previous Yield"), value=_t("Rice"))

    if st.button(_t("Query Remote Telemetry & Run Models"), type="primary"):
        with st.spinner(_t("Fetching data from remote meteorology and soil mapping API endpoints...")):
            
            # Pass the lat and lon values to the updated API function
            env_package = fetch_automated_environmental_data(lat_input, lon_input)
            
            if env_package.get("error") and "Demo Mode" not in env_package["error"]:
                st.error(_t(env_package["error"]))
                return
                
        st.success(_t("Telemetry download successful! All regional environmental elements is found."))
        
        st.subheader(f"📊 {_t('Retrieved Location Environment Profile')}")
        w_col, s_col = st.columns(2)
        with w_col:
            st.metric(_t("Live Air Temperature"), f"{env_package['temperature']} °C")
            st.metric(_t("Relative Air Humidity"), f"{env_package['humidity']} %")
            st.metric(_t("Surface Wind Speed"), f"{env_package['wind_speed']} m/s")
        with s_col:
            st.metric(_t("Soil N-P-K Composition"), f"{env_package['n']} - {env_package['p']} - {env_package['k']} mg/kg")
            st.metric(_t("Calculated Soil pH"), f"{env_package['ph']}")
            st.metric(_t("Volumetric Soil Moisture"), f"{env_package['moisture']} %")

        # --- ML EXECUTION BLOCK ---
        model = load_crop_classifier()
        features = np.array([[
            env_package['n'], env_package['p'], env_package['k'], 
            env_package['temperature'], env_package['humidity'], 
            env_package['ph'], env_package['moisture']
        ]])
        
        predicted_crops = []
        if model:
            try:
                probabilities = model.predict_proba(features)[0]
                top_indices = np.argsort(probabilities)[-5:][::-1]
                
                for i in top_indices:
                    numerical_class = model.classes_[i]
                    crop_name = CROP_DICT.get(numerical_class, "Unknown Crop")
                    predicted_crops.append(crop_name)
                    
            except Exception as e:
                st.error(f"{_t('Machine Learning execution error')}: {e}")
                predicted_crops = ["Rice", "Wheat", "Maize", "Lentil", "Cotton"] 
        else:
            st.warning(_t("No .pkl model found. Using fallback prediction array."))
            predicted_crops = ["Rice", "Wheat", "Maize", "Lentil", "Cotton"]

        # --- AI Financial Generation & Sorting ---
        st.subheader(f"💰 {_t('Top Recommended Crops (Ranked by Profitability)')}")
        
        with st.spinner(_t("Calculating market economics and sorting by maximum profit...")):
            financial_reports = []
            
            for crop in predicted_crops:
                report = generate_crop_financials(crop, land_size)
                try:
                    profit_val = float(report.get("profit_percentage", "0").replace("%", "").strip())
                except ValueError:
                    profit_val = 0.0
                    
                financial_reports.append({
                    "crop_name": crop,
                    "profit_val": profit_val,
                    "data": report
                })
                
            financial_reports = sorted(financial_reports, key=lambda x: x["profit_val"], reverse=True)

        for idx, item in enumerate(financial_reports, 1):
            translated_crop_name = _t(item["crop_name"])
            financials = item["data"]
            
            expander_title = f"{_t('Recommendation')} {idx}: {translated_crop_name} ({_t('Est. Profit')}: {item['profit_val']}%)"
            
            with st.expander(expander_title):
                c1, c2, c3 = st.columns(3)
                c1.metric(_t("Est. Total Input Cost"), financials.get("estimated_input_cost", "N/A"))
                c2.metric(_t("Expected Gross Revenue"), financials.get("expected_revenue", "N/A"))
                c3.metric(_t("Projected Profit Margin"), financials.get("profit_percentage", "N/A"))
                
                st.markdown(f"**🔗 {_t('Production Reference Query')}:** {_t('Search YouTube for')} `\"{financials.get('youtube_query')}\"` {_t('to view verified production protocols.')}")
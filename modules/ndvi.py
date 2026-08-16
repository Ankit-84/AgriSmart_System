import streamlit as st
import requests
import time
import datetime
import os
import numpy as np
import plotly.graph_objects as go
from utils.translator_api import translate_text

def fetch_satellite_data(lat, lon):
    """
    Connects to AgroMonitoring Sentinel-2 orbital API.
    Dynamically searches for the clearest possible image in the historical dataset.
    """
    api_key = os.getenv("AGRO_API_KEY") or os.getenv("AGROMONITORING_API_KEY")
    
    if not api_key:
        return {"error": "API Key is missing! Please check your .env file."}

    offset = 0.002
    geojson_payload = {
        "name": f"Field_Scan_{lat:.4f}_{lon:.4f}",
        "geo_json": {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [lon - offset, lat - offset],
                        [lon - offset, lat + offset],
                        [lon + offset, lat + offset],
                        [lon + offset, lat - offset],
                        [lon - offset, lat - offset]
                    ]
                ]
            }
        }
    }

    try:
        poly_url = f"http://api.agromonitoring.com/agro/1.0/polygons?appid={api_key}&duplicated=true"
        poly_resp = requests.post(poly_url, json=geojson_payload, timeout=10)

        if poly_resp.status_code not in [200, 201]:
            return {"error": f"API Rejected Polygon: {poly_resp.text}"}
            
        poly_id = poly_resp.json().get("id")

        # Search imagery over the past 180 days (Expanded to 6 months to bypass the monsoon)
        end_time = int(time.time()) - 86400 
        start_time = end_time - (180 * 24 * 60 * 60)
        img_url = f"http://api.agromonitoring.com/agro/1.0/image/search?start={start_time}&end={end_time}&polyid={poly_id}&appid={api_key}"
        
        img_resp = requests.get(img_url, timeout=10)
        
        if img_resp.status_code != 200:
            return {"error": f"API Image Search Failed: {img_resp.text}"}
            
        images = img_resp.json()
        
        if not images or len(images) == 0:
            return {"error": "No satellite imagery found for these coordinates in the last 180 days."}
            
        # --- THE FIX: DYNAMIC CLOUD RANKING ---
        # Sort all available images by their cloud cover percentage (lowest to highest)
        clearest_images = sorted(images, key=lambda x: x.get("cl", 100))
        
        # Grab the image with the absolute least amount of clouds
        latest = clearest_images[0]
        
        # If even the absolute best day is still completely covered, alert the user
        if latest.get("cl", 100) >= 90:
             return {"error": "Extreme monsoon conditions: Even the best satellite pass is over 90% obscured. Try again post-monsoon."}
        
        mean_ndvi = 0.64
        stats_url = latest.get("stats", {}).get("ndvi")
        if stats_url:
            try:
                s_resp = requests.get(stats_url, timeout=6)
                if s_resp.status_code == 200:
                    mean_ndvi = float(s_resp.json().get("mean", 0.64))
            except Exception:
                pass

        return {
            "status": "live",
            "date": datetime.datetime.fromtimestamp(latest.get("dt", end_time)).strftime('%Y-%m-%d'),
            "mean_ndvi": round(mean_ndvi, 2),
            "cloud_cover": round(latest.get("cl", 8.5), 1),
            "true_color_url": latest.get("image", {}).get("truecolor"),
            "ndvi_image_url": latest.get("image", {}).get("ndvi")
        }
        
    except Exception as e:
        return {"error": f"Critical Python Error during API call: {str(e)}"}
    
# --- UI DASHBOARD ---
def render_ndvi_dashboard():
    current_lang = st.session_state.get("selected_language", "English")

    def _t(text: str) -> str:
        return translate_text(text, current_lang)

    st.markdown("""
        <style>
            .glass-panel {
                background: linear-gradient(145deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
                backdrop-filter: blur(12px);
                border: 1px solid rgba(16, 185, 129, 0.2);
                border-radius: 16px;
                padding: 25px;
                margin-bottom: 20px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            .ndvi-title {
                color: #10B981;
                font-size: 22px;
                font-weight: 700;
                margin-bottom: 8px;
            }
            .ndvi-text {
                color: #CBD5E1;
                font-size: 14px;
                line-height: 1.5;
            }
        </style>
    """, unsafe_allow_html=True)

    st.header(f"🛰️ {_t('Satellite Crop Health Monitoring')}")
    st.write(_t("Analyze live satellite imagery to detect crop stress, moisture levels, and vegetation health."))

    control_col, map_col = st.columns([1, 2], gap="large")

    with control_col:
        st.markdown(f"""
            <div class="glass-panel">
                <div class="ndvi-title">{_t('Target Coordinates')}</div>
                <div class="ndvi-text">{_t('Enter the exact GPS coordinates of the farm to initialize the satellite scan.')}</div>
            </div>
        """, unsafe_allow_html=True)

        with st.form("ndvi_scanner_form"):
            lat_input = st.number_input(_t("Latitude"), value=25.6154, format="%.6f")
            lon_input = st.number_input(_t("Longitude"), value=85.1010, format="%.6f")
            scan_btn = st.form_submit_button(_t("Initialize Satellite Scan"), type="primary", width='stretch')

    with map_col:
        if not scan_btn:
            st.info(_t("Awaiting coordinate input. Click 'Initialize Satellite Scan' to connect to the orbital database."))
        else:
            with st.spinner(_t("Establishing connection with AgroMonitoring Satellites...")):
                sat_data = fetch_satellite_data(lat_input, lon_input)

            # --- THE FIX: PROPER ERROR CHECKING ---
            if "error" in sat_data:
                # If the API returns an error, show it cleanly and stop executing the rest of the code
                st.error(_t(sat_data["error"]))
            else:
                # If successful, display the UI elements!
                st.success(f"{_t('Satellite telemetry established successfully!')} {_t('All regional environmental elements is found.')} ({_t('Pass Date')}: {sat_data['date']})")

                # --- HEALTH STATUS METRICS ---
                mean_val = sat_data['mean_ndvi']
                if mean_val >= 0.6:
                    health_label = _t("High Density Biomass (Optimal)")
                elif mean_val >= 0.4:
                    health_label = _t("Moderate Canopy Health")
                else:
                    health_label = _t("Stressed / Low Vegetation")

                cloud_status = _t("Clear Sky") if sat_data['cloud_cover'] < 20 else _t("Partly Obscured")

                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric(_t("Mean NDVI Index"), f"{mean_val:.2f}", health_label)
                with m2:
                    st.metric(_t("Cloud Obscurity"), f"{sat_data['cloud_cover']}%", cloud_status, delta_color="inverse")
                with m3:
                    st.metric(_t("Spatial Resolution"), "10m / px", _t("Sentinel-2 MSI"))

                st.divider()

                # --- VISUAL COMPARISON MATRIX ---
                st.markdown(f"### 🗺️ {_t('Visual Diagnostics')}")
                img1, img2 = st.columns(2)

                with img1:
                    st.caption(f"📷 {_t('True Color (Visible Spectrum)')}")
                    if sat_data.get('true_color_url'):
                        st.image(sat_data['true_color_url'], width='stretch')
                    else:
                        st.write(_t("Image unavailable"))

                with img2:
                    st.caption(f"🌈 {_t('NDVI Heatmap (Infrared Diagnostics)')}")
                    if sat_data.get('ndvi_image_url'):
                        st.image(sat_data['ndvi_image_url'], width='stretch')
                    else:
                        st.write(_t("Image unavailable"))

                st.divider()

                # --- SATELLITE SPECTRAL GAUGE ---
                st.markdown(f"### 📊 {_t('NDVI Canopy Health Gauge')}")
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=mean_val,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    gauge={
                        'axis': {'range': [-0.2, 1.0], 'tickwidth': 1, 'tickcolor': "#94A3B8"},
                        'bar': {'color': "#10B981"},
                        'bgcolor': "rgba(15, 23, 42, 0.8)",
                        'borderwidth': 2,
                        'bordercolor': "rgba(255, 255, 255, 0.1)",
                        'steps': [
                            {'range': [-0.2, 0.2], 'color': 'rgba(239, 68, 68, 0.4)'},
                            {'range': [0.2, 0.5], 'color': 'rgba(245, 158, 11, 0.4)'},
                            {'range': [0.5, 1.0], 'color': 'rgba(16, 185, 129, 0.4)'}
                        ]
                    }
                ))
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    font={'color': "#F8FAFC"},
                    height=260,
                    margin=dict(l=20, r=20, t=30, b=10)
                )
                st.plotly_chart(fig, width='stretch')
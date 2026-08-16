import base64
import os
import requests
import openai
import json
from dotenv import load_dotenv
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
DATAGOV_API_KEY = os.getenv("DATAGOV_API_KEY")

client = openai.OpenAI(api_key=OPENAI_API_KEY)
PLANT_ID_API_KEY = os.getenv("PLANT_ID_API_KEY")

def identify_plant_disease_api(image_bytes):
    """
    Sends the image to the Plant.id API to identify diseases across thousands of classes.
    """
    if not PLANT_ID_API_KEY:
        return "Error: Plant.id API key is missing from the .env file."

    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    url = "https://plant.id/api/v3/health_assessment?details=disease_details&modifiers=disease_model=full,symptoms=true"
    
    headers = {
        "Api-Key": PLANT_ID_API_KEY,
        "Content-Type": "application/json"
    }
    

    data = {
        "images": [f"data:image/jpeg;base64,{base64_image}"]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        
        # Plant.id v3 often returns 201 Created on successful image processing
        if response.status_code in [200, 201]:
            result = response.json()
            
            # Plant.id v3 nests all analysis data inside a master "result" object
            assessment = result.get("result", {})
            
            # Check if the plant is healthy first
            is_healthy = assessment.get("is_healthy", {}).get("binary", False)
            if is_healthy:
                return "Healthy Plant"
            
            # If diseased, extract the highest probability disease suggestion
            diseases = assessment.get("disease", {}).get("suggestions", [])
            if diseases:

                top_disease = diseases[0].get("name", "Unknown Disease Pathogen")
                return top_disease
                
            return "No specific disease identified by the API."
        else:
            return f"API Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Network Request Failed: {str(e)}"

def fetch_automated_environmental_data(lat, lon):
    """
    Chains Weather and Geographic Soil APIs sequentially using location coordinates.
    """
    if not WEATHER_API_KEY:
        return {
            "temperature": 29.2, "humidity": 74, "wind_speed": 11.2,
            "n": 85, "p": 40, "k": 45, "ph": 6.4, "moisture": 52,
            "error": "Demo Mode: API keys uninitialized"
        }

    weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
    try:
        w_response = requests.get(weather_url, timeout=10)
        if w_response.status_code != 200:
            return {"error": "Location data untraceable by geocoding layer."}
            
        w_data = w_response.json()
        
        
        weather_metrics = {
            "temperature": w_data["main"]["temp"],
            "humidity": w_data["main"]["humidity"],
            "wind_speed": w_data["wind"]["speed"]
        }

        # Query SoilGrids for pH, Nitrogen, SOC, and CEC at the 0-5cm depth
        soil_url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}&property=phh2o&property=nitrogen&property=soc&property=cec&depth=0-5cm&value=mean"
        s_response = requests.get(soil_url, timeout=10)
        
        if s_response.status_code == 200:
            s_data = s_response.json()
            layers = s_data.get("properties", {}).get("layers", [])

            def get_soil_value(prop_name):
                try:
                    
                    layer = next(l for l in layers if l["name"] == prop_name)
                    
                    raw_value = layer["depths"][0]["values"]["mean"]
                    
                    d_factor = layer.get("unit_measure", {}).get("d_factor", 1)
                    return raw_value / d_factor
                except (StopIteration, KeyError, TypeError, IndexError):
                    return None

            ph = get_soil_value("phh2o") or 6.5
            
            # SoilGrids Nitrogen is returned in cg/kg. Multiply by 10 for standard mg/kg
            n_cg_kg = get_soil_value("nitrogen")
            n = (n_cg_kg * 10) if n_cg_kg else 85
            
            # Derive a dynamic proxy for P and K since SoilGrids does not track them
            soc = get_soil_value("soc") or 40
            cec = get_soil_value("cec") or 15
            
            parsed_soil = {
                "ph": round(ph, 1),
                "n": round(n),
                "p": round(soc * 0.8), 
                "k": round(cec * 2.5), 
                "moisture": 48 
            }
        else:
            parsed_soil = {"ph": 6.2, "n": 80, "p": 38, "k": 42, "moisture": 50}

        combined_data = {**weather_metrics, **parsed_soil, "error": None}
        return combined_data

    except Exception as e:
        return {"error": f"Network interruption during query execution: {str(e)}"}


def generate_crop_financials(crop_name, land_size):
    """Uses OpenAI to dynamically generate an economic projection report for the selected crop."""
    prompt = f"""
    Act as an expert agricultural economist specializing in Indian farming systems.
    The farmer wants to cultivate '{crop_name}' across an area of {land_size} acres.
    Calculate realistic economic projections for this production season.
    Provide the output strictly as a valid JSON object with these exact keys:
    {{
        "estimated_input_cost": "Total estimated cost in INR format (e.g., ₹75,000)",
        "expected_revenue": "Expected gross market revenue from the harvest in INR format",
        "profit_percentage": "Net profit margin percentage (e.g., 45%)",
        "youtube_query": "Optimized precise search keywords to look up cultivation guides for this crop"
    }}
    Do not add any text before or after the JSON pattern.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {
            "estimated_input_cost": "Unavailable", 
            "expected_revenue": "Unavailable", 
            "profit_percentage": "N/A",
            "youtube_query": f"{crop_name} farming methods"
        }


def analyze_disease_with_llm(disease_label):
    """Uses OpenAI to construct complete chemical and organic therapeutic protocols for a disease."""
    prompt = f"""
    A plant leaf sample has been diagnosed with '{disease_label}'.
    Provide a comprehensive management strategy covering:
    1. Natural / Organic Remedies: Eco-friendly solutions, biological controls, or traditional methods.
    2. Chemical Pesticides: Precise active ingredients or specific pesticide options recommended by agricultural standards.
    3. Prevention Techniques: Long-term cultural practices to avoid recurrence.
    Keep the tone highly practical and helpful for a farmer.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error retrieving therapeutic report: {str(e)}"
    


def fetch_live_mandi_price(state, crop_name):
    """
    Fetches real-time daily wholesale prices for ALL districts in a state.
    """
    DATAGOV_API_KEY = os.getenv("DATAGOV_API_KEY")
    if not DATAGOV_API_KEY:
        return {"data": [], "status": "error", "message": "API Key Missing"}

    clean_state = state.strip().title()
    clean_crop = crop_name.strip().title()

    url = "https://api.data.gov.in/resource/35985678-0d79-46b4-9ed6-6f13308a1d24"
    
    payload = {
        "api-key": DATAGOV_API_KEY,
        "format": "json",
        "filters[State]": clean_state,
        "filters[Commodity]": clean_crop,
        "sort[Arrival_Date]": "desc", 
        "limit": "100"  # Increased from 1 to 100 to get statewide data
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, params=payload, headers=headers, timeout=50, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            records = data.get("records", [])
            
            if records:
                all_market_data = []
                
                for record in records:
                    all_market_data.append({
                        "Arrival Date": record.get('Arrival_Date') or record.get('arrival_date') or 'N/A',
                        "District": record.get('District') or record.get('district') or 'Unspecified',
                        "Market (Mandi)": record.get('Market') or record.get('market') or 'Local Market',
                        "Variety": record.get('Variety') or record.get('variety') or 'Standard',
                        "Min Price (₹/Qtl)": record.get('Min_Price') or record.get('min_price') or 'N/A',
                        "Max Price (₹/Qtl)": record.get('Max_Price') or record.get('max_price') or 'N/A',
                        "Modal Price (₹/Qtl)": record.get('Modal_Price') or record.get('modal_price') or 'N/A'
                    })
                
                return {"data": all_market_data, "status": "success"}
            else:
                return {"data": [], "status": "empty"}
        else:
            return {"data": [], "status": "error", "message": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"Data.gov Network Exception: {str(e)}")
        return {"data": [], "status": "error", "message": "Network Error"}
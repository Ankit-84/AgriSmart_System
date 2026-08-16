from PIL.ImageOps import crop
import streamlit as st
from utils.api import fetch_live_mandi_price
import pandas as pd
import plotly.express as px
from utils.translator_api import translate_text

INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", 
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", 
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", 
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", 
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
]
GOV_COMMODITIES = [
    "Absinthe", "Ajwan", "Alasande Gram", "Almond(Badam)", "Alsandikai", "Amaranthus", 
    "Ambada Seed", "Ambady/Mesta", "Ambady/Mesta/Patson", "Amla(Nelli Kai)", "Amphophalus", 
    "Amranthas Red", "Antawala", "Anthorium", "Apple", "Apricot(Jardalu/Khumani)", 
    "Arecanut(Betelnut/Supari)", "Arhar (Tur/Red Gram)(Whole)", "Arhar Dal(Tur Dal)", 
    "Asalia", "Ashgourd", "Ashwagandha", "Asparagus", "Astera", "Avare Dal", "BOP", 
    "Bael", "Bajra(Pearl Millet/Cumbu)", "Balekai", "Bamboo", "Banana", "Banana - Green", 
    "Barley (Jau)", "Barley(Jau)", "Bay leaf (Tejpatta)", "Bay leaf(Tejpatta)", "Beans", 
    "Beaten Rice", "Beetroot", "Bengal Gram Dal (Chana Dal)", "Bengal Gram Dal(Chana Dal)", 
    "Bengal Gram(Gram)(Whole)", "Ber(Zizyphus/Borehannu)", "Betal Leaves", "Betelnuts", 
    "Bhindi(Ladies Finger)", "Bhui Amlaya", "Big Gram", "Binoula", "Bitter gourd", 
    "Black Gram (Urd Beans)(Whole)", "Black Gram Dal (Urd Dal)", "Black Gram Dal(Urd Dal)", 
    "Black Gram(Urd Beans)(Whole)", "Black pepper", "Borehannu", "Bottle gourd", "Brahmi", 
    "Bran", "Brinjal", "Broken Rice", "Broomstick(Flower Broom)", "Bull", "Bullar", 
    "Bunch Beans", "Butter", "Cabbage", "Calendula", "Calf", "Cane", "Capsicum", 
    "Cardamom", "Cardamoms", "Carnation", "Carrot", "Cashew Kernnel", "Cashewnuts", 
    "Castor Oil", "Castor Seed", "Cauliflower", "Chakotha", "Chapparad Avare", 
    "Chennangi (Whole)", "Chennangi Dal", "Cherry", "Chikoos(Sapota)", "Chili Red", 
    "Chilly Capsicum", "Chow Chow", "Chrysanthemum", "Chrysanthemum(Loose)", 
    "Cinamon(Dalchini)", "Cloves", "Cluster beans", "Coca", "Cock", "Cocoa", "Coconut", 
    "Coconut Oil", "Coconut Seed", "Coffee", "Colacasia", "Copra", "Coriander(Leaves)", 
    "Corriander seed", "Cotton", "Cotton Seed", "Cow", "Cowpea (Lobia/Karamani)", 
    "Cowpea(Lobia/Karamani)", "Cowpea(Veg)", "Cucumbar(Kheera)", "Cummin Seed(Jeera)", 
    "Custard Apple (Sharifa)", "Custard Apple(Sharifa)", "Daila(Chandni)", "Dal (Avare)", 
    "Dalda", "Delha", "Dhaincha", "Drumstick", "Dry Chillies", "Dry Fodder", "Dry Grapes", 
    "Duck", "Duster Beans", "Egg", "Egyptian Clover(Barseem)", "Elephant Yam (Suran)", 
    "Elephant Yam(Suran)/Amorphophallus", "Field Pea", "Fig(Anjura/Anjeer)", "Firewood", 
    "Fish", "Flower Broom", "Foxtail Millet(Navane)", "French Beans (Frasbean)", 
    "French Beans(Frasbean)", "Galgal(Lemon)", "Garlic", "Ghee", "Giloy", "Gingelly Oil", 
    "Ginger(Dry)", "Ginger(Green)", "Gladiolus Bulb", "Gladiolus Cut Flower", "Goat", 
    "Gram Raw(Chholia)", "Gramflour", "Grapes", "Green Avare (W)", "Green Avare(W)", 
    "Green Chilli", "Green Fodder", "Green Gram (Moong)(Whole)", "Green Gram Dal (Moong Dal)", 
    "Green Gram(Moong)(Whole)", "Green Peas", "Ground Nut Oil", "Ground Nut Seed", 
    "Groundnut", "Groundnut (Split)", "Groundnut pods (raw)", "Groundnut pods(raw)", 
    "Groundnut(Split)", "Guar", "Guar Seed(Cluster Beans Seed)", "Guava", "Gudmar", 
    "Guggal", "Gur(Jaggery)", "Gurellu", "Haralekai", "He Buffalo", "Hen", "Hippe Seed", 
    "Honey", "Honge seed", "Hybrid Cumbu", "Indian Beans (Seam)", "Indian Beans(Seam)", 
    "Indian Colza(Sarson)", "Isabgul (Psyllium)", "Isabgul(Psyllium)", "Jack Fruit", 
    "Jack Fruit(Ripe)", "Jaffri", "Jaggery", "Jamamkhan", "Jamun(Narale Hannu)", "Jarbara", 
    "Jasmine", "Javi", "Jowar(Sorghum)", "Jute", "Jute Seed", "Kabuli Chana(Chickpeas-White)", 
    "Kacholam", "Kakada", "Kalmegh", "Kankambra", "Karamani", "Karbuja(Musk Melon)", 
    "Kartali (Kantola)", "Kartali(Kantola)", "Kharif Mash", "Khoya", "Kinnow", "Knool Khol", 
    "Kodo Millet(Varagu)", "Kooth", "Kuchur", "Kulthi(Horse Gram)", "Kutki", "Ladies Finger", 
    "Lak(Teora)", "Leafy Vegetable", "Lemon", "Lentil (Masur)(Whole)", "Lentil(Masur)(Whole)", 
    "Lilly", "Lime", "Linseed", "Lint", "Litchi", "Little gourd (Kundru)", "Little gourd(Kundru)", 
    "Long Melon(Kakri)", "Lotus", "Lotus Sticks", "Lukad", "Mace", "Mahedi", "Mahua", 
    "Mahua Seed(Hippe seed)", "Maida Atta", "Maize", "Mango", "Mango (Raw-Ripe)", 
    "Mango(Raw-Ripe)", "Maragensu", "Marasebu", "Marget", "Marigold(Calcutta)", 
    "Marigold(loose)", "Mash", "Mashrooms", "Masur Dal", "Mataki", "Methi Seeds", 
    "Methi(Leaves)", "Millets", "Mint(Pudina)", "Moath Dal", "Mousambi(Sweet Lime)", 
    "Muesli", "Muleti", "Mustard", "Mustard Oil", "Myrobolan(Harad)", "Nearle Hannu", 
    "Neem Seed", "Nelli Kai", "Niger Seed (Ramtil)", "Niger Seed(Ramtil)", "Nutmeg", 
    "Onion", "Onion Green", "Orange", "Orchid", "Other Pulses", 
    "Other green and fresh vegetables", "Ox", "Paddy(Basmati)", "Paddy(Common)", 
    "Paddy(Dhan)(Basmati)", "Paddy(Dhan)(Common)", "Palash flowers", "Papaya", 
    "Papaya (Raw)", "Papaya(Raw)", "Patti Calcutta", "Pea Pod/Pea Cod/हरी मटर", 
    "Peach", "Pear(Marasebu)", "Peas Wet", "Peas cod", "Peas(Dry)", 
    "Pegeon Pea (Arhar Fali)", "Pegeon Pea(Arhar Fali)", "Pepper garbled", 
    "Pepper ungarbled", "Persimon(Japani Fal)", "Pigs", "Pineapple", "Plum", 
    "Pointed gourd (Parval)", "Pointed gourd(Parval)", "Polherb", "Pomegranate", 
    "Potato", "Pumpkin", "Pundi", "Pundi Seed", "Pupadia", "Raddish", 
    "Ragi (Finger Millet)", "Ragi(Finger Millet)", "Raibel", "Rajgir", "Ram", 
    "Rat Tail Radish (Mogari)", "Rat Tail Radish(Mogari)", "Ratanjot", "Raya", 
    "Red Gram", "Red gram split/Arhar dal/Tur dal", "Red gram/Arhar/Tur(whole)", 
    "Resinwood", "Riccbcan", "Rice", "Ridgeguard(Tori)", "Rose(Local)", 
    "Rose(Loose))", "Rose(Tata)", "Round gourd", "Rubber", "Sabu Dan", 
    "Safflower", "Saffron", "Sajje", "Same/Savi", "Sanai/Sunhemp", "Sarasum", 
    "Season Leaves", "Seemebadnekai", "Seetapal", "Sesamum(Sesame,Gingelly,Til)", 
    "She Buffalo", "She Goat", "Sheep", "Siddota", "Skin And Hide", "Snakeguard", 
    "Soanf", "Soapnut(Antawala/Retha)", "Soji", "Sompu", "Soyabean", "Spinach", 
    "Spiny Gourd / Kartali(Kantola)", "Sponge gourd", "Squash(Chappal Kadoo)", 
    "Sugar", "Sugarcane", "Sunflower", "Sunflower Seed", "Sunflower/Sunflower Seed", 
    "Sunhemp", "Suram", "Surat Beans (Papadi)", "Surat Beans(Papadi)", 
    "Suva (Dill Seed)", "Suva(Dill Seed)", "Suvarna Gadde", "Sweet Potato", 
    "Sweet Pumpkin", "T.V. Cumbu", "Tamarind Fruit", "Tamarind Seed", "Tapioca", 
    "Taramira", "Tea", "Tender Coconut", "Thinai (Italian Millet)", 
    "Thinai(Italian Millet)", "Thogrikai", "Thondekai", "Tinda", "Tobacco", 
    "Tomato", "Torchwood", "Toria", "Tube Flower", "Tube Rose(Double)", 
    "Tube Rose(Loose)", "Tube Rose(Single)", "Tulip", "Turmeric", "Turmeric (raw)", 
    "Turmeric(raw)", "Turnip", "Walnut", "Water Melon", "Wheat", "Wheat Atta", 
    "White Muesli", "White Peas", "White Pumpkin", "Wood", "Wool", "Yam", 
    "Yam (Ratalu)", "Yam(Ratalu)", "basil", "buttery", "dhawai flowers", 
    "dried mango", "gulli", "karanja seeds", "kutki", "liquor turmeric", 
    "mango powder", "nigella", "nigella seeds", "pippali", "poppy seeds", 
    "sanay", "spikenard", "stevia", "stone pulverizer", "vadang"
]

def render_market_prices():
    # Fetch the dynamically selected language from the session state
    current_lang = st.session_state.get("selected_language", "English")
    
    # Internal helper to translate strings in this module
    def _t(text: str) -> str:
        return translate_text(text, current_lang)

    st.header(f"📈 {_t('Statewide Mandi Market Analytics')}")
    st.write(_t("Analyze the latest wholesale trading rates across all districts in your selected state."))
    
    with st.form("market_price_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            state = st.selectbox(_t("Select State"), INDIAN_STATES, index=3) 
            
        with col2:
            selected_crop = st.selectbox(_t("Select Commodity"), GOV_COMMODITIES, index=0)
        
        submit_btn = st.form_submit_button(_t("Fetch Statewide Market Rates"), type="primary", width='stretch')
        
    if submit_btn:
        with st.spinner(f"{_t('Querying Government databases for')} {selected_crop} {_t('across all districts in')} {state}..."):
            market_response = fetch_live_mandi_price(state, selected_crop)
            
            if market_response["status"] == "success":
                df = pd.DataFrame(market_response["data"])
                
                # We must convert the price strings into actual numbers so we can do math and chart them
                df["Numeric Price"] = pd.to_numeric(df["Modal Price (₹/Qtl)"], errors='coerce')
                valid_prices = df.dropna(subset=["Numeric Price"])
                
                if not valid_prices.empty:
                    st.success(f"{_t('Successfully retrieved and analyzed market data for')} {selected_crop} {_t('in')} {state}!")
                    
                    # --- 1. TOP-LEVEL KPI METRICS ---
                    max_price = valid_prices["Numeric Price"].max()
                    min_price = valid_prices["Numeric Price"].min()
                    avg_price = valid_prices["Numeric Price"].mean()
                    
                    max_district = valid_prices.loc[valid_prices["Numeric Price"].idxmax(), "District"]
                    min_district = valid_prices.loc[valid_prices["Numeric Price"].idxmin(), "District"]
                    
                    kpi1, kpi2, kpi3 = st.columns(3)
                    kpi1.metric(f"🔥 {_t('Most Profitable Mandi')}", f"₹{max_price:,.0f}", f"📍 {max_district}", delta_color="normal")
                    kpi2.metric(f"📊 {_t('State Average')}", f"₹{avg_price:,.0f}", _t("Modal Baseline"), delta_color="off")
                    kpi3.metric(f"📉 {_t('Lowest Rate')}", f"₹{min_price:,.0f}", f"📍 {min_district}", delta_color="inverse")
                    
                    st.divider()

                    st.markdown(f"### 📋 {_t('Raw Market Ledger')}")
                    # Drop the temporary numeric column before showing the table to the user
                    st.dataframe(
                        df.drop(columns=["Numeric Price"]).sort_values(by="Arrival Date", ascending=False),
                        width='stretch',
                        hide_index=True,
                        height=400
                    )

                    st.divider()
                    st.markdown(f"### 📈 {_t('District Price Comparison')}")
                                            
                    # Sort data to show the highest paying districts first
                    chart_data = valid_prices.sort_values(by="Numeric Price", ascending=False).head(15)
                                            
                    # Build a sleek Plotly Bar Chart
                    fig = px.bar(
                        chart_data, 
                        x="District", 
                        y="Numeric Price", 
                        color="Numeric Price",
                        color_continuous_scale="Viridis", # Gives a great green/blue futuristic gradient
                        text_auto='.0f',
                        hover_data={"Market (Mandi)": True, "Numeric Price": True}
                    )
                    
                    fig.update_layout(
                        xaxis_title=_t("District"), 
                        yaxis_title=_t("Price (₹ / Quintal)"), 
                        template="plotly_dark", # Matches your premium dark theme
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                    
                    st.plotly_chart(fig, width='stretch')
                else:
                    st.warning(_t("Data retrieved, but no numeric prices were available to visualize today."))
                
            elif market_response["status"] == "empty":
                st.warning(f"{_t('No recent wholesale trades found for')} '{selected_crop}' {_t('in')} {state}.")
            else:
                st.error(f"{_t('API Error')}: {market_response.get('message', _t('Unknown Error'))}")
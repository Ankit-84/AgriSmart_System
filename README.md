🌱 AgriSmart System
AgriSmart is a next-generation, AI-powered agricultural technology platform designed to empower farmers with precision farming data, satellite telemetry, and real-time government scheme access. Built entirely in Python, this platform eliminates the need for manual data entry and complex local machine learning models by leveraging large language models (LLMs) and orbital APIs.

Once the system initializes, all required environmental elements is found and processed in real-time, delivering actionable insights directly to the user.

✨ Key Features
🛰️ Satellite Crop Health Monitoring (NDVI): Integrates the AgroMonitoring API to fetch 10m/px Sentinel-2 satellite imagery. It automatically filters out heavy monsoon cloud cover to generate accurate Normalized Difference Vegetation Index (NDVI) heatmaps, diagnosing crop stress from space.

🌾 AI Crop & Economic Predictor: Replaces traditional .pkl machine learning models with OpenAI's zero-shot classification. It automatically fetches GPS-based weather and soil telemetry, analyzes it through GPT-4o-mini, and ranks the top 5 most viable crops by projected profit margin.

🏛️ Live Government Scheme Desk: An autonomous Retrieval-Augmented Generation (RAG) agent that actively scrapes official Indian government databases (.gov.in and .nic.in). It answers farmer queries with strict factual accuracy and provides direct download links to official subsidy PDFs.

🌍 Universal Accessibility: Features real-time, dynamic translation into all 22 Scheduled Languages of India, ensuring zero language barriers for regional farmers.

🛠️ Technology Stack
Frontend: Streamlit (Python)

AI Engine: OpenAI API (GPT-4o-mini, Zero-Shot Classification, Vision)

Orbital Telemetry: AgroMonitoring API (Sentinel-2 Data)

Live Web Scraping: DuckDuckGo Search (DDGS)

Translation Engine: Google Translator (via deep-translator)

Data Visualization: Plotly

🚀 Installation & Usage
1. Clone the repository

Bash
git clone https://github.com/Ankit-84/AgriSmart_System.git
cd AgriSmart_System
2. Set up your environment variables
Create a .env file in the root directory and securely add your API keys:

Plaintext
OPENAI_API_KEY="your_openai_key_here"
WEATHER_API_KEY="your_openweathermap_key_here"
AGRO_API_KEY="your_agromonitoring_key_here"
3. Install dependencies

Bash
pip install -r requirements.txt
4. Run the application

Bash
streamlit run app.py
👨‍💻 About the Developer
Developed by Ankit Kumar, a Computer Science and Engineering student at the National Institute of Technology Nagaland (Batch 2024-2028). This project serves as a capstone in applying full-stack engineering, cloud deployments, and artificial intelligence to solve real-world agricultural challenges in India, joining a portfolio of other robust applications including the Tech Avinya 2025 portal and the Wanderlust platform.

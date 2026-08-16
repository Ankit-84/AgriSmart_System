import streamlit as st
import os
from openai import OpenAI
from ddgs import DDGS
from utils.translator_api import translate_text

# --- API CONFIGURATION ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def fetch_live_gov_data(query):
    """
    Silently searches the internet, restricting results ONLY to official Indian 
    Government websites (.gov.in / .nic.in). 
    """
    ddgs = DDGS()
    
    # 1. Search for live webpage information (restricted to gov sites)
    web_query = f"{query} site:gov.in OR site:nic.in"
    try:
        # Fetch top 4 most relevant government webpages
        web_results = ddgs.text(web_query, max_results=4)
    except Exception:
        web_results = []
        
    # 2. Search specifically for official government PDFs
    pdf_query = f"{query} filetype:pdf site:gov.in OR site:nic.in"
    try:
        # Fetch top 3 official government PDF links
        pdf_results = ddgs.text(pdf_query, max_results=3)
    except Exception:
        pdf_results = []
        
    return web_results, pdf_results

def query_live_agent(user_query, web_data, target_lang="English"):
    """Uses OpenAI GPT-4o-mini to synthesize the live search results into a clean answer in the chosen language."""
    if not OPENAI_API_KEY:
        return "Error: OPENAI_API_KEY environment variable is missing."
        
    if not web_data:
        return "I could not find any live official government data for this specific query. Please try rephrasing."
        
    # Build the context string from the live search results
    context = "LIVE GOVERNMENT SEARCH RESULTS:\n\n"
    for res in web_data:
        context += f"Source Title: {res.get('title')}\nURL: {res.get('href')}\nInformation: {res.get('body')}\n\n"
        
    system_instruction = (
        "You are an expert agricultural advisor for Indian farmers. "
        "You must answer the user's question using STRICTLY the provided 'LIVE GOVERNMENT SEARCH RESULTS'. "
        "Summarize the scheme details, eligibility, and financial benefits clearly. "
        "DO NOT invent or guess any information. If the exact answer is not in the search results, say 'Official data for this specific detail is currently unavailable.' "
        "Always cite the exact government URL (from the context) at the bottom of your response. "
        f"CRITICAL RULE: You MUST write your entire final response natively in {target_lang}."
    )
    
    user_prompt = f"Context:\n{context}\n\nFarmer's Question: {user_query}"
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1 # Low temperature ensures strict factual accuracy
        )
        return response.choices[0].message.content
        
    except Exception as e:
        return f"OpenAI Generation Error: {str(e)}"

# --- STREAMLIT UI ---
def render_rag_agent():
    # Fetch the dynamically selected language from the session state
    current_lang = st.session_state.get("selected_language", "English")
    
    # Internal helper to translate strings in this module
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
            .chat-title {
                color: #10B981;
                font-size: 22px;
                font-weight: 700;
                margin-bottom: 5px;
            }
            .chat-subtitle {
                color: #CBD5E1;
                font-size: 14px;
                line-height: 1.6;
            }
            .pdf-box {
                background-color: rgba(59, 130, 246, 0.1);
                border-left: 4px solid #3B82F6;
                padding: 15px;
                border-radius: 8px;
                margin-top: 15px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.header(f"🏛️ {_t('Live Government Scheme Desk')}")
    
    st.markdown(f"""
        <div class="glass-panel">
            <div class="chat-title">{_t('Live Internet Agent')}</div>
            <div class="chat-subtitle">{_t('This assistant actively searches verified government databases (gov.in) in real-time to fetch accurate eligibility rules and official PDF guidelines for any Indian agricultural scheme.')}</div>
        </div>
    """, unsafe_allow_html=True)

    # Initialize session state for chat
    if "live_messages" not in st.session_state:
        st.session_state.live_messages = [
            {"role": "assistant", "content": _t("Namaste! I am connected to live government servers. What scheme can I look up for you?")}
        ]

    # Render previous chat history
    for message in st.session_state.live_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # If we saved PDF links from a previous search, render them below the assistant's message
            if message["role"] == "assistant" and "pdfs" in message and message["pdfs"]:
                st.markdown(f"<div class='pdf-box'><b>📎 {_t('Official Government Documents Found')}:</b></div>", width='stretch')
                for pdf in message["pdfs"]:
                    st.link_button(f"📄 {_t('Download')}: {pdf['title'][:50]}...", pdf['href'])

    # React to user input
    if prompt := st.chat_input(_t("E.g., Give me details about the PM-KISAN scheme")):
        # 1. Display User Message
        st.chat_message("user").markdown(prompt)
        st.session_state.live_messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            # 2. Fetch Live Web & PDF Data
            with st.spinner(_t("Scanning verified government servers (.gov.in) for live data...")):
                web_results, pdf_results = fetch_live_gov_data(prompt)
                
            # 3. Generate Answer using OpenAI (Passing current_lang to enforce native language generation)
            with st.spinner(_t("Synthesizing official guidelines...")):
                response = query_live_agent(prompt, web_results, target_lang=current_lang)
                st.markdown(response)
                
                # 4. Display Direct PDF Download Buttons
                if pdf_results:
                    st.markdown(f"<div class='pdf-box'><b>📎 {_t('Official Government Documents Found')}:</b></div>", width='stretch')
                    for pdf in pdf_results:
                        st.link_button(f"📄 {_t('Download')}: {pdf['title'][:50]}...", pdf['href'])
        
        # 5. Save everything to chat history so it doesn't disappear
        st.session_state.live_messages.append({
            "role": "assistant", 
            "content": response,
            "pdfs": pdf_results  # We store the PDFs here so they reload properly
        })
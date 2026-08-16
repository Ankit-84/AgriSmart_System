import streamlit as st
import os
from openai import OpenAI
from gtts import gTTS
import io
from utils.translator_api import translate_text

# Map UI language selection to gTTS language codes
GTTS_LANG_MAP = {
    "English": "en",
    "Hindi": "hi",
    "Bengali": "bn",
    "Assamese": "bn",  # Assamese isn't natively in standard gTTS; Bengali is phonetically closest
    "Marathi": "mr",
    "Telugu": "te"
}

def render_chatbot():
    # Fetch the dynamically selected language from the session state
    current_lang = st.session_state.get("selected_language", "English")
    
    # Internal helper to translate strings in this module
    def _t(text: str) -> str:
        return translate_text(text, current_lang)

    st.header(f"🤖 {_t('AgriBot Conversational Assistant')}")
    st.write(_t("Ask questions about irrigation, specialized treatments, fertilizer dosing, or active local market rates by typing or speaking."))
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error(_t("OpenAI API key missing from environment settings. Please check your .env file layout."))
        return

    client = OpenAI(api_key=api_key)
    
    # Initialize chat history database state array if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "system", 
                "content": "You are an expert agronomy consultant assisting Indian farmers. Give clear, direct advice on crop care, fertilizer volumes, market conditions, and soil treatment. Keep answers structural, precise, and practical. If the user asks a question in Hindi or a regional dialect, you must reply back in that exact same language using the native script."
            },
            # Translate the welcome message dynamically upon first load
            {"role": "assistant", "content": _t("Welcome! I am connected via OpenAI to your diagnostic metrics. How can I assist you with your farming decisions today?")}
        ]
        
    # Display previous chat history (skipping the system instruction)
    for index, msg in enumerate(st.session_state.messages):
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                
                # If it's an assistant message, provide a Text-to-Speech button option
                if msg["role"] == "assistant":
                    # Generate a unique key for each message button
                    if st.button(_t("🔊 Listen to Response"), key=f"tts_{index}"):
                        with st.spinner(_t("Generating audio narration...")):
                            try:
                                # Dynamically set the TTS language based on user selection
                                tts_lang_code = GTTS_LANG_MAP.get(current_lang, "hi")
                                tts = gTTS(text=msg["content"], lang=tts_lang_code, slow=False)
                                
                                audio_buffer = io.BytesIO()
                                tts.write_to_fp(audio_buffer)
                                audio_buffer.seek(0) 
                                
                                st.audio(audio_buffer, format="audio/mp3", autoplay=True)
                                
                            except Exception as tts_err:
                                st.error(f"{_t('Free TTS Engine Error')}: {str(tts_err)}")

    user_text = st.chat_input(_t("Enter your agriculture question here..."))
    
    with st.expander(f"🎙️ {_t('Click here to speak instead of typing')}"):
        audio_file = st.audio_input(_t("Record your question in your native language:"))
    
    final_prompt = None
    
    if user_text:
        final_prompt = user_text
    elif audio_file:
        if "last_audio" not in st.session_state or st.session_state.last_audio != audio_file:
            with st.spinner(_t("Processing voice input through Whisper translation...")):
                try:
                    audio_file.name = "audio.wav"
                    transcription = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                    if transcription.text.strip():
                        final_prompt = transcription.text
                        st.info(f"🎙️ **{_t('Voice Recognized')}:** {final_prompt}")
                    else:
                        st.warning(_t("Audio detected, but no clear speech could be understood."))
                        
                    st.session_state.last_audio = audio_file
                except Exception as audio_err:
                    st.error(f"{_t('Failed to process speech transcription')}: {str(audio_err)}")
                    st.session_state.last_audio = audio_file


    if final_prompt:
        st.session_state.messages.append({"role": "user", "content": final_prompt})
        
        with st.chat_message("user"):
            st.write(final_prompt)
            
        with st.chat_message("assistant"):
            with st.spinner(_t("Analyzing agricultural knowledge arrays...")):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=st.session_state.messages
                    )
                    reply = response.choices[0].message.content
                    st.write(reply)
                    
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"{_t('Failed to reach chat engine')}: {str(e)}")
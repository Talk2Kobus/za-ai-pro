# app.py
import streamlit as st
from toon import to_toon, from_toon
import markdown
import sqlite3
from datetime import datetime
import io
import base64
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import get rigidity
import os

st.set_page_config(page_title="ZA AI Pro", layout="centered")
st.title("ZA AI Pro")
st.caption(f"{datetime.now().strftime('%I:%M %p')} | South Africa | @{os.getenv('USER', 'KobusvWyk')}")

if "messages" not in st.session_state:
    st.session_state.messages = []

user_input = st.chat_input("Ask in English or Afrikaans...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # MOCK AI RESPONSE (replace with your Go backend or Grok)
    mock_toon = f"""
[1]{{answer}}|
**Hallo @KobusvWyk!**  
Jou vraag: *{user_input}*  
Tyd: {datetime.now().strftime('%d %b %Y %I:%M %p')}  
Antwoord in Afrikaans: *Hier is jou antwoord in pragtige Afrikaans.*
"""
    st.session_state.messages.append({"role": "assistant", "content": mock_toon})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            data = from_toon(msg["content"])
            answer = data[0].get("answer", "")
            st.markdown(answer)
        else:
            st.write(msg["content"])
# app.py — FULL PRO ZA AI
import streamlit as st
from toon import from_toon
import markdown
import sqlite3
from datetime import datetime
import os
import httpx
import base64
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet

# --- INIT ---
DB = "history.db"
def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY, user TEXT, input TEXT, output TEXT, time TEXT)")
    conn.commit(); conn.close()
init_db()

st.set_page_config(page_title="ZA AI Pro", layout="centered")
st.title("ZA AI Pro")
st.caption(f"{datetime.now().strftime('%I:%M %p')} • South Africa • @KobusvWyk")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- MOCK AI (Vervang met Grok later) ---
def call_ai(prompt):
    return f"""
[1]{{title|answer}}|
**ZA AI Pro**  
*Vraag:* {prompt}  
*Antwoord in Afrikaans:* Hier is ’n pragtige, ryk TOON-geformatteerde respons met **vet**, *kursief*, en selfs tabelle as jy later wil hê.  
Jou tyd: {datetime.now().strftime('%d %b %Y %H:%M')}
"""

# --- CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            data = from_toon(msg["content"])[0]
            st.markdown(data.get("answer", ""))
        else:
            st.write(msg["content"])

if prompt := st.chat_input("Vra in Afrikaans of Engels..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Dink in Afrikaans..."):
            toon = call_ai(prompt)
            data = from_toon(toon)[0]
            answer = data.get("answer", "")
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": toon})

            # Save
            conn = sqlite3.connect(DB)
            conn.execute("INSERT INTO chat (user, input, output, time) VALUES (?,?,?,?)",
                        ("KobusvWyk", prompt, toon, datetime.now().isoformat()))
            conn.commit()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("PDF"):
            buf = io.BytesIO()
            doc = SimpleDocTemplate(buf, pagesize=A4)
            story = [Paragraph(answer, getSampleStyleSheet()["Normal"])]
            doc.build(story)
            st.download_button("Laai PDF", buf.getvalue(), "ai_antwoord.pdf", "application/pdf")
    with col2:
        if st.button("Afrikaans Stem"):
            st.info("Stem sintese kom binnekort — Coqui TTS word gelaai...")

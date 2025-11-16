# app.py — ZA AI Pro (Full Pro, Fixed, Deploy-Ready)
import streamlit as st
from datetime import datetime
import sqlite3
import os
import io
import base64
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# --- CONFIG ---
DB_PATH = "chat_history.db"
st.set_page_config(page_title="ZA AI Pro", layout="centered", initial_sidebar_state="collapsed")

# --- INIT DB ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            input TEXT,
            output TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- MOCK AI (Replace with Grok API later) ---
def call_ai(prompt: str) -> str:
    return f"""
[1]{{title|answer}}|
**ZA AI Pro – 16 Nov 2025**  
*Jou vraag:* {prompt}  
*Antwoord in Afrikaans:*  
Hier is ’n **volledige TOON-geformatteerde** respons.  
Jy kan later tabelle, stem, en PDF byvoeg.  
**Tyd:** {datetime.now().strftime('%d %b %Y %H:%M')} SAST  
**Gebruiker:** @KobusvWyk  
**Land:** South Africa  
"""

# --- RENDER TOON ---
def render_toon(toon_str: str) -> str:
    try:
        # Safe TOON parse
        data = __import__("toon").from_toon(toon_str)
        return data[0].get("answer", toon_str)
    except:
        return toon_str

# --- PDF EXPORT ---
def export_pdf(answer: str):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=40)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("ZA AI Pro – Antwoord", styles["Title"]))
    story.append(Spacer(1, 12))

    # Answer
    for line in answer.split("\n"):
        if line.strip():
            story.append(Paragraph(line, styles["Normal"]))
        else:
            story.append(Spacer(1, 6))

    doc.build(story)
    return buffer.getvalue()

# --- UI ---
st.title("ZA AI Pro")
st.caption(f"{datetime.now().strftime('%I:%M %p')} • South Africa • @KobusvWyk")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.markdown(render_toon(msg["content"]), unsafe_allow_html=True)
        else:
            st.write(msg["content"])

# Input
if prompt := st.chat_input("Vra in Afrikaans of Engels..."):
    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # AI response
    with st.chat_message("assistant"):
        with st.spinner("Dink in Afrikaans..."):
            toon_response = call_ai(prompt)
            rendered = render_toon(toon_response)
            st.markdown(rendered, unsafe_allow_html=True)

            # Save to DB
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "INSERT INTO history (user, input, output, timestamp) VALUES (?, ?, ?, ?)",
                ("KobusvWyk", prompt, toon_response, datetime.now().isoformat())
            )
            conn.commit()
            conn.close()

            st.session_state.messages.append({"role": "assistant", "content": toon_response})

    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("PDF", key="pdf"):
            pdf_data = export_pdf(rendered)
            st.download_button(
                label="Laai PDF",
                data=pdf_data,
                file_name=f"ZA_AI_Antwoord_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf"
            )
    with col2:
        if st.button("Afrikaans Stem", key="tts"):
            st.info("Afrikaans stem sintese kom binnekort (Coqui TTS).")
    with col3:
        if st.button("WhatsApp Audio", key="wa"):
            st.info("WhatsApp stemnota word gestuur... (Twilio + TTS)")

# --- Sidebar: History ---
with st.sidebar:
    st.header("Geskiedenis")
    conn = sqlite3.connect(DB_PATH)
    history = conn.execute(
        "SELECT input, timestamp FROM history WHERE user = ? ORDER BY timestamp DESC LIMIT 5",
        ("KobusvWyk",)
    ).fetchall()
    conn.close()

    for q, t in history:
        st.caption(f"_{t.split('T')[1][:5]}_")
        st.write(q[:50] + ("..." if len(q) > 50 else ""))

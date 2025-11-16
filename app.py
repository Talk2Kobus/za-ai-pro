# app.py — ZA AI Pro with FREE Afrikaans Voice (Piper TTS)
import streamlit as st
import sqlite3
from datetime import datetime
import io
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import subprocess
import os

# ========================================
# 1. TOON PARSER (No library)
# ========================================
def from_toon(toon_str: str):
    try:
        pattern = r"\[1\]\{(.*?)\}\|\s*(.*)"
        match = re.search(pattern, toon_str, re.DOTALL)
        if not match:
            return [{"answer": toon_str.strip()}]
        keys = [k.strip() for k in match.group(1).split("|") if k.strip()]
        values_part = match.group(2).strip()
        values = [v.strip() for v in re.split(r'(?<!\\)\|', values_part)]
        if len(keys) != len(values):
            return [{"answer": toon_str.strip()}]
        return [dict(zip(keys, values))]
    except:
        return [{"answer": toon_str.strip()}]

# ========================================
# 2. DATABASE
# ========================================
DB_PATH = "chat_history.db"
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT, input TEXT, output TEXT, timestamp TEXT)""")
    conn.commit()
    conn.close()
init_db()

# ========================================
# 3. MOCK AI
# ========================================
def call_ai(prompt: str) -> str:
    return f"""
[1]{{title|answer}}|
**ZA AI Pro**  
*Jou vraag:* {prompt}  
**Antwoord in Afrikaans:**  
Goeiemôre @KobusvWyk!  
Hier is jou antwoord in pragtige Afrikaans.  
Jy kan dit nou **hoor** deur op die stemknoppie te klik.  
**Tyd:** {datetime.now().strftime('%d %b %Y %H:%M')} SAST  
**Land:** South Africa  
"""

# ========================================
# 4. PDF EXPORT
# ========================================
def export_pdf(text: str):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=50)
    styles = getSampleStyleSheet()
    story = [Paragraph("ZA AI Pro – Antwoord", styles["Title"]), Spacer(1, 20)]
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("**") and line.endswith("**"):
            story.append(Paragraph(f"<b>{line[2:-2]}</b>", styles["Heading2"]))
        elif line:
            story.append(Paragraph(line, styles["Normal"]))
        else:
            story.append(Spacer(1, 6))
    doc.build(story)
    return buffer.getvalue()

# ========================================
# 5. VOICE: Piper TTS (Free, Legal, ZA Afrikaans)
# ========================================
@st.cache_data(ttl=3600)
def text_to_speech_afrikaans(text: str):
    try:
        # Clean text for speech
        clean = re.sub(r'\*\*|\*|_|\[|\]|\{|\}|\|', '', text)
        clean = re.sub(r'\n+', '. ', clean).strip()
        if not clean:
            return None

        # Use Piper (installed via piper-tts)
        model = "en_ZA-lessac-medium.onnx"  # Built-in ZA voice
        cmd = ["piper", "--model", model, "--output_file", "-"]
        process = subprocess.run(
            cmd,
            input=clean.encode('utf-8'),
            capture_output=True,
            check=True
        )
        return process.stdout
    except Exception as e:
        st.error(f"Stem fout: {e}")
        return None

# ========================================
# 6. UI
# ========================================
st.set_page_config(page_title="ZA AI Pro", layout="centered")
st.title("ZA AI Pro")
st.caption(f"{datetime.now().strftime('%I:%M %p')} • South Africa • @KobusvWyk")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            data = from_toon(msg["content"])[0]
            answer = data.get("answer", "")
            st.markdown(answer, unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

# Input
if prompt := st.chat_input("Vra in Afrikaans of Engels..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Dink..."):
            toon_response = call_ai(prompt)
            data = from_toon(toon_response)[0]
            answer = data.get("answer", "")
            st.markdown(answer, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": toon_response})

            # Save
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO history (user, input, output, timestamp) VALUES (?,?,?,?)",
                        ("KobusvWyk", prompt, toon_response, datetime.now().isoformat()))
            conn.commit()

    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("PDF", key="pdf"):
            st.download_button("Laai PDF", export_pdf(answer), "ZA_AI.pdf", "application/pdf")
    with col2:
        if st.button("Afrikaans Stem", key="tts"):
            with st.spinner("Praat..."):
                audio = text_to_speech_afrikaans(answer)
                if audio:
                    st.audio(audio, format="audio/wav")
                    st.success("Luister nou!")
    with col3:
        st.button("WhatsApp (kom binnekort)")

# Sidebar: History
with st.sidebar:
    st.header("Geskiedenis")
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT input, timestamp FROM history ORDER BY timestamp DESC LIMIT 5").fetchall()
    for q, t in rows:
        time_str = t.split("T")[1][:5] if "T" in t else "?"
        st.caption(f"**{time_str}**")
        st.write(q[:40] + ("..." if len(q) > 40 else ""))
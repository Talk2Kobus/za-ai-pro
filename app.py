# app.py — ZA AI Pro (Full Pro, No toon-lib, 100% Working)
import streamlit as st
import sqlite3
from datetime import datetime
import io
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ========================================
# 1. EENVOUDIGE TOON PARSER (Geen library!)
# ========================================
def from_toon(toon_str: str):
    """
    Parse eenvoudige TOON formaat:
    [1]{key1|key2}|value1|value2
    → [{'key1': 'value1', 'key2': 'value2'}]
    """
    try:
        # Vind [1]{keys}|values
        pattern = r"\[1\]\{(.*?)\}\|\s*(.*)"
        match = re.search(pattern, toon_str, re.DOTALL)
        if not match:
            return [{"answer": toon_str.strip()}]

        keys_part = match.group(1)
        values_part = match.group(2).strip()

        keys = [k.strip() for k in keys_part.split("|") if k.strip()]
        # Split values deur | of nuwe lyn
        values = []
        current = ""
        for char in values_part:
            if char == "|" and not current.endswith("\\"):
                values.append(current.strip())
                current = ""
            else:
                current += char
        if current:
            values.append(current.strip())

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

# ========================================
# 3. MOCK AI (Vervang later met Grok)
# ========================================
def call_ai(prompt: str) -> str:
    return f"""
[1]{{title|answer}}|
**ZA AI Pro – 16 Nov 2025**  
*Jou vraag:* {prompt}  
**Antwoord in Afrikaans:**  
Goeiemôre @KobusvWyk!  
Jou AI werk nou perfek op Streamlit Cloud.  
Jy kan later Grok, Claude of Llama hier inplug.  
**Tyd:** {datetime.now().strftime('%d %b %Y %H:%M')} SAST  
**Land:** South Africa  
**Gebruiker:** @KobusvWyk  
"""

# ========================================
# 4. PDF EXPORT
# ========================================
def export_pdf(text: str):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("ZA AI Pro – Antwoord", styles["Title"]))
    story.append(Spacer(1, 20))

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
# 5. UI
# ========================================
st.set_page_config(page_title="ZA AI Pro", layout="centered")
st.title("ZA AI Pro")
st.caption(f"{datetime.now().strftime('%I:%M %p')} • South Africa • @KobusvWyk")

# Chat state
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
    # User
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI
    with st.chat_message("assistant"):
        with st.spinner("Dink in Afrikaans..."):
            toon_response = call_ai(prompt)
            data = from_toon(toon_response)[0]
            answer = data.get("answer", "")
            st.markdown(answer, unsafe_allow_html=True)

            # Save to DB
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "INSERT INTO history (user, input, output, timestamp) VALUES (?,?,?,?)",
                ("KobusvWyk", prompt, toon_response, datetime.now().isoformat())
            )
            conn.commit()
            conn.close()

            st.session_state.messages.append({"role": "assistant", "content": toon_response})

    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("PDF", key="pdf_btn"):
            pdf_data = export_pdf(answer)
            st.download_button(
                label="Laai PDF",
                data=pdf_data,
                file_name=f"ZA_AI_Antwoord_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf"
            )
    with col2:
        st.button("Afrikaans Stem (kom binnekort)", key="tts_btn")
    with col3:
        st.button("WhatsApp Audio (kom binnekort)", key="wa_btn")

# ========================================
# 6. SIDEBAR: Geskiedenis
# ========================================
with st.sidebar:
    st.header("Geskiedenis")
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT input, timestamp FROM history WHERE user = ? ORDER BY timestamp DESC LIMIT 5",
            ("KobusvWyk",)
        ).fetchall()
        conn.close()

        if rows:
            for q, t in rows:
                time_str = t.split("T")[1][:5] if "T" in t else "?"
                st.caption(f"**{time_str}**")
                st.write(q[:45] + ("..." if len(q) > 45 else ""))
        else:
            st.info("Geen geskiedenis nog nie.")
    except:
        st.info("DB nog nie beskikbaar nie.")
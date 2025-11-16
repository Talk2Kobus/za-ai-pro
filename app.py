import streamlit as st
from datetime import datetime

st.set_page_config(page_title="ZA AI Pro", layout="centered")

st.title("🔥 ZA AI Pro")
st.caption(f"🕒 {datetime.now().strftime('%I:%M %p')} • 🇿🇦 South Africa • 👤 @KobusvWyk")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Vra in Engels of Afrikaans..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Dink..."):
            # Hier kom later jou Grok/Go API
            response = f"""
**Hallo Kobus!**  
Jou vraag: *{prompt}*  
Tyd: {datetime.now().strftime('%d %b %Y %H:%M')}  
Antwoord in Afrikaans: _Hier is ’n pragtige voorbeeld van TOON-gebaseerde respons._  
👇 Jou AI is nou lewendig!
"""
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.balloons()

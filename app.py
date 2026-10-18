import streamlit as st
import litellm
import os
from dotenv import load_dotenv

# Load environment variables dari .env
load_dotenv()

# Set konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Spark AI Platform",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Spark AI Gateway & Hub")
st.caption("Platform Terpadu Akses Multi-LLM (ChatGPT, Claude, Gemini)")

# Sidebar untuk Pengaturan & Pilihan Model
with st.sidebar:
    st.header("⚙️ Pengaturan Spark")
    
    # Pilih Model AI
    selected_model = st.selectbox(
        "Pilih Model AI:",
        ["gpt-4o", "claude-3.5-sonnet", "gemini-flash"]
    )
    
    # Parameter Temperatur
    temperature = st.slider("Temperature:", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
    
    st.divider()
    if st.button("Hapus Riwayat Chat"):
        st.session_state.messages = []
        st.rerun()

# Inisialisasi Riwayat Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan Riwayat Chat di UI
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input Pesan Pengguna
if prompt := st.chat_input("Ketik pesan untuk Spark..."):
    # Simpan dan tampilkan pesan user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Kirim ke LiteLLM Router
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Menggunakan LiteLLM completion
            response = litellm.completion(
                model=selected_model,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                temperature=temperature,
                stream=True
            )
            
            # Stream jawaban secara real-time
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                full_response += content
                message_placeholder.markdown(full_response + "▌")
                
            message_placeholder.markdown(full_response)
            
            # Simpan jawaban assistant ke session
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Gagal memanggil model {selected_model}: {str(e)}")

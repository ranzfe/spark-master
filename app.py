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

# --- INJEKSI CSS UNTUK TAMPILAN STYLE V0 (DARK MINIMALIST) ---
st.markdown("""
<style>
    /* Latar belakang utama serba hitam */
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    /* Navbar Atas */
    .nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 20px;
        border-bottom: 1px solid #1a1a1a;
        margin-bottom: 30px;
    }
    .nav-logo {
        font-weight: bold;
        font-size: 20px;
        letter-spacing: 1px;
    }
    .nav-links {
        display: flex;
        gap: 20px;
        color: #888888;
        font-size: 14px;
    }
    
    /* Hero Title di tengah */
    .hero-title {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 700;
        margin-top: 40px;
        margin-bottom: 20px;
        letter-spacing: -1px;
    }
    
    /* Subtitle Badge */
    .badge-container {
        display: flex;
        justify-content: center;
        margin-bottom: 15px;
    }
    .badge {
        background-color: #111111;
        border: 1px solid #222222;
        border-radius: 20px;
        padding: 6px 16px;
        font-size: 13px;
        color: #cccccc;
    }
    
    /* Sembunyikan elemen bawaan streamlit yang mengganggu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>

<!-- Navbar Atas -->
<div class="nav-container">
    <div class="nav-logo">⚡ SPARK</div>
    <div class="nav-links">
        <span>Templates</span>
        <span>Enterprise</span>
        <span>Pricing</span>
        <span>FAQ</span>
    </div>
</div>

<!-- Badge & Judul Utama -->
<div class="badge-container">
    <div class="badge">⚡ Powered by Spark Multi-LLM Gateway</div>
</div>
<h1 class="hero-title">What do you want to create?</h1>
""", unsafe_allow_html=True)

# --- SIDEBAR UNTUK PENGATURAN MODEL ---
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
    if st.button("Hapus Riwayat Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Inisialisasi Riwayat Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- TEMPLATE SUGGESTION BUTTONS (Pills) ---
if len(st.session_state.messages) == 0:
    st.write("")
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])
    with col1:
        if st.button("✉️ Contact Form"):
            st.session_state.prompt_trigger = "Buatkan kode HTML/CSS contact form yang modern."
    with col2:
        if st.button("🖼️ Image Editor"):
            st.session_state.prompt_trigger = "Buat aplikasi web Image Editor sederhana."
    with col3:
        if st.button("🎮 Mini Game"):
            st.session_state.prompt_trigger = "Buatkan game Tic-Tac-Toe berbasis HTML/JS."
    with col4:
        if st.button("📈 Finance Calc"):
            st.session_state.prompt_trigger = "Buatkan kalkulator keuangan sederhana."

# --- TAMPILKAN RIWAYAT CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Cek apakah ada prompt dari tombol suggestion
prompt_input = st.session_state.pop("prompt_trigger", None)

# --- INPUT CHAT UTAMA ---
if prompt := (st.chat_input("Ask Spark to build...") or prompt_input):
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

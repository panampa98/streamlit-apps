import streamlit as st
from streamlit_chat import message
import google.generativeai as genai

import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

from datetime import datetime
from pytz import timezone

tz = timezone("America/Lima")

cred_dict = json.loads(st.secrets["firebase_service_account"])
cred = credentials.Certificate(cred_dict)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Configuración inicial
st.set_page_config(page_title="Chat con Gemini", page_icon="🤖")
st.title("🤖 Chat con Gemini (Google AI)")

# -------- REGISTRO DE USUARIO --------
if "user_email" not in st.session_state:
    email = st.text_input("Introduce tu correo para comenzar:", key="email_input")
    if email and "@" in email:
        st.session_state.user_email = email.lower().strip()
        st.rerun()
    st.stop()

email = st.session_state.user_email
st.success(f"Sesión iniciada como: {email}")

# -------- CONSULTA Y ACTUALIZACIÓN DE TOKENS --------
def check_tokens(email):
    doc_ref = db.collection("users").document(email)
    doc = doc_ref.get()

    today_str = datetime.now(tz).strftime("%Y-%m-%d")

    if doc.exists:
        data = doc.to_dict()
        last_used = data.get("last_used", "")
        daily_tokens = data.get("daily_tokens", 0)
        total_tokens = data.get("total_tokens", 0)

        # Reiniciar contador si cambió el día
        if last_used != today_str:
            daily_tokens = 0

        if daily_tokens >= 3:
            return False, daily_tokens, total_tokens

        # Incrementar tokens
        daily_tokens += 1
        total_tokens += 1
    else:
        # Crear nuevo usuario
        daily_tokens = 1
        total_tokens = 1

    doc_ref.set({
        "email": email,
        "daily_tokens": daily_tokens,
        "total_tokens": total_tokens,
        "last_used": today_str
    })
    return True, daily_tokens, total_tokens

# -------- CHAT --------
# Cargar tu API KEY (puedes usar st.secrets o una variable de entorno)
genai.configure(api_key=st.secrets.get("GEMINI_API_KEY", None))

# # Lista los modelos disponibles
# models = genai.list_models()

# for model in models:
#     print("📦 Nombre:", model.name)
#     print("🧠 Soporta generate_content:", "generateContent" in model.supported_generation_methods)
#     print("---")

# Crear modelo
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")

# Inicializar historial si no existe
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar el chat
for msg in st.session_state.messages:
    message(msg["content"], is_user=(msg["role"] == "user"))

# Input del usuario
prompt = st.chat_input("Escribe tu mensaje...")

# Procesar si hay input
if prompt:
    allowed, today_count, total = check_tokens(email)

    if not allowed:
        st.warning("⚠️ Límite diario de 3 mensajes alcanzado. Inténtalo mañana.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        message(prompt, is_user=True)
        try:
            response = model.generate_content(prompt)
            reply = response.text
        except Exception as e:
            reply = f"⚠️ Error: {e}"
        st.session_state.messages.append({"role": "ai", "content": reply})
        message(reply, is_user=False)


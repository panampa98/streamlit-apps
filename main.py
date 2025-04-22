import streamlit as st
from streamlit_chat import message
import google.generativeai as genai

# Configuración inicial
st.set_page_config(page_title="Chat con Gemini", page_icon="🤖")
st.title("🤖 Chat con Gemini (Google AI)")

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

# Input del usuario
prompt = st.chat_input("Escribe tu mensaje...")

# Procesar entrada
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    try:
        response = model.generate_content(prompt)
        reply = response.text
    except Exception as e:
        reply = f"⚠️ Error: {e}"
    st.session_state.messages.append({"role": "ai", "content": reply})

# Mostrar el chat
for msg in st.session_state.messages:
    message(msg["content"], is_user=(msg["role"] == "user"))

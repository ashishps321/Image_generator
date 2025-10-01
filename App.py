import streamlit as st
from io import BytesIO
from PIL import Image
import requests
from PyPDF2 import PdfReader
import docx

# -------------------
# Config
# -------------------

HF_API_KEY = st.secrets.get("HF_API_KEY")
if not HF_API_KEY:
    st.error("Hugging Face API key not found! Add it to Streamlit Secrets.")
    st.stop()

# -------------------
# Functions
# -------------------

# Text generation using HF Inference API
def generate_text(prompt: str):
    API_URL = "https://api-inference.huggingface.co/models/gpt2"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    if response.status_code == 200:
        try:
            output = response.json()
            if isinstance(output, list) and "generated_text" in output[0]:
                return output[0]["generated_text"]
            return str(output)
        except:
            return str(output)
    else:
        return f"⚠️ Text generation failed. Status code: {response.status_code}"

# Image generation using Stable Diffusion HF model
def generate_image(prompt: str):
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    if response.status_code == 200:
        try:
            img = Image.open(BytesIO(response.content))
            return img
        except:
            return None
    else:
        return None

# -------------------
# Initialize session
# -------------------
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# -------------------
# Page Config
# -------------------
st.set_page_config(page_title="HF Chat & Image Bot", page_icon="🤖", layout="wide")

# -------------------
# Sidebar
# -------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=80)
    st.title("💬 HF Chat & Image Bot")
    st.markdown("---")
    st.subheader("⚡ About")
    st.write("AI-powered assistant for text chat and image generation using Hugging Face models.")
    st.subheader("🛠 Options")
    if st.button("🧹 Clear Chat"):
        st.session_state["chat_history"] = []
    st.markdown("---")
    st.caption("🚀 Developed by Ashish")

# -------------------
# Custom CSS
# -------------------
st.markdown("""
<style>
.user-bubble {background-color:#0d6efd;color:white;padding:12px;border-radius:18px;max-width:70%;margin-left:auto;margin-bottom:8px;word-wrap:break-word;}
.bot-bubble {background-color:#e9ecef;color:#212529;padding:12px;border-radius:18px;max-width:70%;margin-right:auto;margin-bottom:8px;word-wrap:break-word;}
.title {text-align:center;font-size:32px;font-weight:bold;color:#0d47a1;margin-bottom:4px;}
.tagline {text-align:center;font-size:14px;color:#6c757d;margin-bottom:15px;}
.stTextInput {flex:1;}
.stButton > button {background-color:#0d6efd;color:white;padding:0.6rem 1rem;border-radius:8px;border:none;cursor:pointer;font-weight:bold;}
.stButton > button:hover {background-color:#0b5ed7;}
</style>
""", unsafe_allow_html=True)

# -------------------
# Title & Description
# -------------------
st.markdown('<div class="title">🤖 HF Chat & Image Bot</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">Chat or generate images using Hugging Face models</div>', unsafe_allow_html=True)

# -------------------
# File Upload Section
# -------------------
uploaded_files = st.file_uploader(
    "📎 Upload files (txt, pdf, docx, images) before asking question",
    type=["txt","pdf","docx","png","jpg","jpeg","bmp"],
    accept_multiple_files=True
)

# -------------------
# Chat Input Form
# -------------------
with st.form("chat_form"):
    user_input = st.text_input("💭 Type your message:", key="user_input_key")
    generate_img = st.checkbox("Generate Image from prompt")
    submit_button = st.form_submit_button("Ask")

# -------------------
# Process Query
# -------------------
if submit_button and user_input.strip():
    combined_input = user_input.strip()
    st.session_state["chat_history"].append(("user", combined_input))

    # Process uploaded files
    if uploaded_files:
        file_texts = []
        for file in uploaded_files:
            if file.type == "text/plain":
                file_texts.append(file.read().decode("utf-8"))
            elif file.type == "application/pdf":
                reader = PdfReader(file)
                text = "".join([page.extract_text() + "\n" for page in reader.pages])
                file_texts.append(text)
            elif file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                               "application/msword"]:
                doc = docx.Document(file)
                text = "\n".join([p.text for p in doc.paragraphs])
                file_texts.append(text)
            elif file.type.startswith("image/"):
                st.session_state["chat_history"].append(("user", f"[Uploaded Image] {file.name}"))
        if file_texts:
            combined_files_text = "\n".join(file_texts)
            st.session_state["chat_history"].append(("user", f"[Uploaded Files] {combined_files_text}"))
            combined_input += "\n" + combined_files_text

    # Generate Image or Text
    if generate_img:
        img = generate_image(combined_input)
        if img:
            st.session_state["chat_history"].append(("bot", f"[Generated Image for prompt: {combined_input}]"))
            st.image(img, caption=combined_input)
        else:
            st.session_state["chat_history"].append(("bot", "⚠️ Failed to generate image."))
    else:
        response = generate_text(combined_input)
        st.session_state["chat_history"].append(("bot", response))

# -------------------
# Display chat just above input
# -------------------
for role, msg in st.session_state["chat_history"]:
    if role == "user":
        st.markdown(f'<div class="user-bubble">{msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-bubble">{msg}</div>', unsafe_allow_html=True)

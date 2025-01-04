import streamlit as st
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

import os
import shutil
from pathlib import Path

# Initialize Session State
if 'index' not in st.session_state:
    st.session_state.index = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_file' not in st.session_state:
    st.session_state.current_file = None

# Configure Page
st.set_page_config(
    page_title="PDF Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Sidebar for User Inputs
st.sidebar.header("Cofigurations")
groq_api_key = st.sidebar.text_input("Enter Groq API Key",type="password")

@st.cache_resource
def initialize_settings():
    """Initialize LLM and Embedding Settings"""
    Settings.llm =  Groq(
        model="llama3-70b-8192",
        api_key=groq_api_key
    )

    Settings.embed_model= HuggingFaceEmbedding(
        model_name="BAAT/bge-small-en-v1.5"
    )

def cleanup_temp_files():
    """Clean up Temporalry directory and files."""
    temp_dir = Path("temp")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

def load_pdf(file_path: str) -> VectorStoreIndex:
    """Load and Index a PDF Document
    
    Args: 
        file_path: PDF file Path

    Returns:
        VectorStoreIndex: Indexed PDF Content
    """
    try:
        with st.spinner("📚 Loading PDF Content"):
            loader = SimpleDirectoryReader(input_files=[file_path])
            documents = loader.load_data()
            return VectorStoreIndex.from_documents(documents)
    except Exception as e:
        st.error(f"Error loading PDF: {str(e)}")
        return None
    

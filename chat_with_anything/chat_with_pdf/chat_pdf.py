import streamlit as st
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core import SimpleDirectoryReader
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
    page_title="PDF Chat",
    page_icon="🤖",
    layout="wide"
)

@st.cache_resource
def initialize_settings():
    """Initialize LLM and embedding settings."""
    Settings.llm = Ollama(
        model="mistral:latest",
        request_timeout=600
    )
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )

def cleanup_temp_files():
    """Clean up temporary directory and files."""
    temp_dir = Path("temp")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

def load_pdf(file_path: str) -> VectorStoreIndex:
    """
    Load and Index a PDF Document
    
    Args:
        file_path: PDF File Path

    Returns:
        VectorStoreIndex: Indexed PDF Content
    """
    try:
        with st.spinner("📚 Loading PDF Content..."):
            loader = SimpleDirectoryReader(input_files=[file_path])  # Fix: Wrap file_path in a list
            documents = loader.load_data()
            return VectorStoreIndex.from_documents(documents)
    except Exception as e:
        st.error(f"Error loading PDF: {str(e)}")
        return None

def save_uploaded_file(uploaded_file):
    """
    Save uploaded file to temporary directory
    
    Args:
        uploaded_file: StreamlitUploadedFile object
    
    Returns:
        str: Path to saved file
    """
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    file_path = temp_dir / uploaded_file.name
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    
    return str(file_path)

def main():
    # Initialize Settings
    initialize_settings()

    # Sidebar
    st.sidebar.header("Configuration")
    uploaded_file = st.sidebar.file_uploader("Upload a PDF", type=["pdf"])

    # Main content
    st.title("🤖 Chat With PDF")
    st.caption(
        """
        Upload a PDF document and chat with its content!
        This app uses Ollama for natural language processing and LlamaIndex for efficient document indexing.           
        """
    )

    # Create a container for chat messages
    chat_container = st.container()

    # Create a container for the input field at the bottom
    input_container = st.container()

    try:
        # Handle file upload
        if uploaded_file:
            # Check if we need to reload the index (new file uploaded)
            if st.session_state.current_file != uploaded_file.name:
                st.session_state.current_file = uploaded_file.name
                st.session_state.index = None
                st.session_state.chat_history = []
                
                # Save and load new file
                file_path = save_uploaded_file(uploaded_file)
                st.session_state.index = load_pdf(file_path)
                
                if st.session_state.index:
                    st.success(f"✅ Successfully loaded {uploaded_file.name}")
                else:
                    st.error("Failed to load the PDF. Please try again with a different file.")
                    return

            # Display Chat History in the chat container
            with chat_container:
                if st.session_state.chat_history:
                    for role, message in st.session_state.chat_history:
                        if role == "user":
                            st.markdown(f"""
                            <div style="display: flex; justify-content: flex-end;">
                                <div style="background-color: #1976d2; color: white; padding: 10px; border-radius: 10px; max-width: 70%;">
                                    {message}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style="display: flex; justify-content: flex-start;">
                                <div style="background-color: #f0f2f6; padding: 10px; border-radius: 10px; max-width: 70%;">
                                    {message}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Add some space after the chat history
                    st.markdown("<br>" * 2, unsafe_allow_html=True)

            # Input field at the bottom
            with input_container:
                st.markdown("<br>" * 2, unsafe_allow_html=True)  # Add some space before input
                user_question = st.text_input(
                    "Ask a question about your PDF",
                    key="user_question",
                    placeholder="Type your question here..."
                )
                
                # Clear chat button
                if st.session_state.chat_history:
                    if st.button("Clear Chat History"):
                        st.session_state.chat_history = []
                        st.rerun()
            
            if user_question and st.session_state.index:
                with st.spinner("🤔 Thinking..."):
                    query_engine = st.session_state.index.as_query_engine()
                    response = query_engine.query(user_question)
                    st.session_state.chat_history.append(("user", user_question))
                    st.session_state.chat_history.append(("assistant", str(response)))
                    st.rerun()  # Rerun to update chat history display

        else:
            st.info("👈 Please upload a PDF document to begin chatting!")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("💡 Tips:\n"
                "- Make sure the PDF is not corrupted\n"
                "- Check if the file is password protected\n"
                "- Try with a different PDF file")
    
    # Cleanup temporary files when the session ends
    st.session_state.on_close = cleanup_temp_files

if __name__ == "__main__":
    main()
import streamlit as st
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings, VectorStoreIndex
from llama_index.readers.github import GithubRepositoryReader, GithubClient
from llama_index.core.node_parser import SimpleNodeParser

from urllib.parse import urlparse
from typing import Tuple, Optional
import time
import os



# Initialize session state
if 'index' not in st.session_state:
    st.session_state.index = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Configure page
st.set_page_config(
    page_title="GitHub Repository Chat",
    page_icon="💬",
    layout="wide"
)

# Initialize LLM and embedding settings
@st.cache_resource
def initialize_settings():
    Settings.llm = Ollama(
        model="mistral:latest",
        request_timeout=600
    )
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )
    

def parse_github_url(url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse a Github URL to extract owner and repo.
    
    Args:
        url (str): GitHub repository URL
        
    Returns:
        Tuple[Optional[str], Optional[str]]: Repository owner and name
    """
    try:
        parsed_url = urlparse(url)
        if 'github.com' not in parsed_url.netloc:
            return None, None
        
        path_parts = parsed_url.path.strip("/").split("/")
        if len(path_parts) >= 2:
            owner = path_parts[0]
            repo = path_parts[1]
            return owner, repo
        return None, None
    except Exception:
        return None, None
    

def load_repository(repo_url: str, owner: str, repo: str):    
    """
    Load and index the GitHub repository.
    
    Args:
        repo_url (str): GitHub repository URL
        
    Returns:
        VectorStoreIndex: Indexed repository content
    """
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        st.warning("⚠️ GitHub token not found. Some private repositories may not be accessible.")
    
    github_client = GithubClient(github_token=github_token, verbose=True)

    # Specify a branch or commit
    default_branch = "main"  # Replace with "master" if your repository uses master
    branch = st.text_input("Enter Branch Name (default: main)", default_branch)


    loader = GithubRepositoryReader(
        github_client=github_client,
        owner=owner,
        repo=repo, 
    )
    
    with st.spinner("📚 Loading repository content..."):
        documents = loader.load_data(branch=branch)
        # parser = SimpleNodeParser()
        # nodes = parser.get_nodes_from_documents(documents)
        index = VectorStoreIndex.from_documents(documents)
        return index

def main():
    # Initialize settings
    initialize_settings()
    
    # Header
    st.title("Chat with GitHub Repository 💬")
    st.caption("""
    Ask questions about any public GitHub repository! This app uses Ollama for natural language processing 
    and LlamaIndex for efficient repository indexing.
    """)
    
    # Repository input
    col1, col2 = st.columns([3, 1])
    with col1:
        repo_url = st.text_input(
            "Enter GitHub Repository URL",
            placeholder="https://github.com/owner/repo",
            key="repo_url"
        )
    
    with col2:
        if st.button("Load Repository", type="primary"):
            st.session_state.index = None
            st.session_state.chat_history = []
    
    # Process repository
    if repo_url:
        owner, repo = parse_github_url(repo_url)
        
        if not owner or not repo:
            st.error("🚫 Invalid GitHub URL. Please provide a URL in the format: https://github.com/owner/repo")
            return
        
        try:
            if not st.session_state.index:
                st.session_state.index = load_repository(repo_url=repo_url, owner=owner, repo=repo)
                st.success(f"✅ Successfully loaded {owner}/{repo}")
        
            # Chat interface
            st.subheader("Ask Questions")
            user_question = st.text_input(
                "What would you like to know about this repository?",
                placeholder="e.g., What is the main purpose of this project?"
            )
            
            if user_question:
                with st.spinner("🤔 Thinking..."):
                    query_engine = st.session_state.index.as_query_engine()
                    response = query_engine.query(user_question)
                    st.session_state.chat_history.append(("user", user_question))
                    st.session_state.chat_history.append(("assistant", str(response)))
            
            # Display chat history
            if st.session_state.chat_history:
                st.subheader("Chat History")
                for role, message in st.session_state.chat_history:
                    if role == "user":
                        st.markdown(f"**You:** {message}")
                    else:
                        st.markdown(f"**Assistant:** {message}")
                        st.markdown("---")
                
                if st.button("Clear Chat History"):
                    st.session_state.chat_history = []
                    st.experimental_rerun()
                    
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("💡 Tips:\n"
                   "- Make sure the repository is public\n"
                   "- Check your internet connection\n"
                   "- Verify the GitHub token if accessing private repositories")

if __name__ == "__main__":
    main()
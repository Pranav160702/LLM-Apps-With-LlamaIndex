# GitHub Repository Chat

This project is a Streamlit-based web application that allows users to chat with a GitHub repository using natural language. The app leverages **Ollama** for natural language understanding and **LlamaIndex** for indexing and querying the repository content.

## Features
- Load and index public or private GitHub repositories.
- Ask questions about the repository's purpose, files, or code.
- Chat interface with chat history.
- Uses Ollama for natural language processing and Hugging Face embeddings.

## Requirements

### Prerequisites
- Python 3.8+
- A valid GitHub token (for accessing private repositories).
- An OpenAI or Ollama API key (for natural language processing).

### Python Packages
- `streamlit`
- `llama-index`
- `huggingface-hub`
- `ollama`

Install all dependencies using:
```bash
pip install streamlit llama-index huggingface-hub ollama
```

## Setup

### Step 1: Clone the Repository
Clone this project repository:
```bash
git clone https://github.com/your-username/github-repo-chat.git
cd github-repo-chat
```

### Step 2: Set Environment Variables
Set the following environment variables:
- `OPENAI_API_KEY`: Your OpenAI or Ollama API key.
- `GITHUB_TOKEN`: Your GitHub personal access token (required for private repositories).

You can add these to a `.env` file or set them in your terminal:
```bash
export OPENAI_API_KEY=your_openai_api_key
export GITHUB_TOKEN=your_github_token
```

### Step 3: Run the Application
Start the Streamlit application:
```bash
streamlit run app.py
```

## Usage
1. Open the application in your browser (default: `http://localhost:8501`).
2. Enter the URL of the GitHub repository you want to interact with.
   - Format: `https://github.com/<owner>/<repo>`
3. Provide a branch name (default is `main`).
4. Ask questions about the repository in natural language.

## Code Overview

### Key Components
1. **GitHub Repository Parsing:**
   - The `parse_github_url` function extracts the repository owner and name from the provided URL.

2. **Repository Loading:**
   - The `GithubRepositoryReader` fetches the repository content (files and code).
   - A `VectorStoreIndex` indexes the repository for efficient querying.

3. **Natural Language Processing:**
   - **Ollama** is used for natural language queries.
   - **Hugging Face** embeddings enable efficient text similarity operations.

4. **Chat Interface:**
   - Displays chat history and handles user interactions.

### Functions
- `initialize_settings()`: Configures the LLM and embedding models.
- `parse_github_url(url)`: Extracts repository owner and name.
- `load_repository(repo_url, owner, repo)`: Loads and indexes the repository content.
- `main()`: Runs the Streamlit app.

## Troubleshooting

### Common Errors
- **"GitHub token not found":** Ensure you set the `GITHUB_TOKEN` environment variable.
- **"Invalid GitHub URL":** Verify the URL is in the format `https://github.com/<owner>/<repo>`.
- **"HTTP Exception":** Check your internet connection and GitHub token permissions.

### Tips
- Use a valid GitHub token with `repo` and `read` permissions for private repositories.
- Ensure the repository uses a supported branch format (e.g., `main` or `master`).

## License
This project is licensed under the MIT License. See the LICENSE file for details.

---

### Example Environment Variables

Create a `.env` file in your project directory with the following content:
```env
OPENAI_API_KEY=your_openai_api_key
GITHUB_TOKEN=your_github_token

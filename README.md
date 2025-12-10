# Agentic Medical Assistant

An agentic application for doctors to record, summarize, and analyze patient conversations with AI assistance.

## Features

- 🎤 **Conversation Recording**: Record and transcribe doctor-patient conversations
- 📝 **AI Summarization**: Automatically summarize conversations and extract key information
- 🗂️ **Patient Management**: Organize patient records and visit history
- 📊 **Pattern Analysis**: Identify patterns in patient history, medication changes, and pathology evolution
- 🏥 **Test Integration**: Upload and parse MRIs, CT scans, blood tests, and other medical tests
- 📄 **PDF Generation**: Generate professional PDF summaries of visits
- 🔍 **Semantic Search**: Search conversations and notes using natural language

## Architecture

- **LLM**: Ollama with Llama 3.1 8B (local)
- **Transcription**: Faster-Whisper (local)
- **Database**: SQLite (structured data) + ChromaDB (semantic search)
- **UI**: Streamlit

## Setup

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Install Ollama**:
```bash
# macOS
brew install ollama

# Or download from https://ollama.ai
```

3. **Pull Llama Model**:
```bash
ollama pull llama3.1:8b
```

4. **Install spaCy Model** (optional, for entity extraction):
```bash
python -m spacy download en_core_web_sm
```

5. **Run the Application**:
```bash
python main.py
```

Or directly:
```bash
streamlit run ui/streamlit_app.py
```

## Usage

1. **Create a Patient**: Register a new patient in the system
2. **Record a Visit**: Upload audio of a conversation, get automatic transcription and summarization
3. **View History**: Browse patient visit history and generate PDF summaries
4. **Upload Tests**: Upload DICOM files (MRIs, scans) or lab results
5. **Pattern Analysis**: Analyze patient evolution over time
6. **Semantic Search**: Search across all conversations and notes using natural language

## Configuration

Edit `config.py` to customize:
- Ollama model and URL
- Whisper model size
- Database paths
- Output directories

## Data Storage

All data is stored locally:
- `data/patients.db` - SQLite database
- `data/chromadb/` - Vector database for semantic search
- `data/patients/` - Patient files and PDFs
- `data/conversations/` - Audio recordings
- `data/tests/` - Medical test files

## Security Note

This is a local-first application. For production use with real patient data:
- Implement encryption at rest
- Add access controls
- Ensure HIPAA compliance
- Use secure authentication

## License

MIT


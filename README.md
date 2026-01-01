# 🤖 Personal AI OS

An Open-Source, Agentic Personal Assistant built with **LangGraph**, **LangChain** & **Local LLMs**

---

## 📌 Overview

**Personal AI OS** is an agent-based personal assistant that leverages open-source LLMs to provide intelligent task automation and natural conversation. It integrates seamlessly with your digital tools while maintaining privacy through local model execution.

### Key Capabilities

- 🗓️ **Manage Google Calendar** - Add, update, and delete events automatically
- 📧 **Send Emails** - Compose and send emails using Gmail API
- 🧠 **Long-term Memory** - Remember personal information using vector-based RAG (Retrieval-Augmented Generation)
- 🔁 **Multi-Tool Orchestration** - Coordinate calendar, email, and reminder actions in sequence
- 💬 **Natural Conversations** - Engage in context-aware dialogue
- 🖥️ **Clean UI** - Streamlit-based interface for easy interaction

### Why Open-Source?

This project is built using **Ollama** (open-source LLMs) — **no OpenAI or paid APIs** — focusing on agent design, orchestration, and real-world tool usage. This approach emphasizes:

- **Privacy** - Models run locally on your machine
- **Cost-effectiveness** - Zero API fees
- **Customization** - Full control over model selection and behavior

> ⚠️ **Note:** Local LLMs may take a few seconds to process responses. This is a conscious design choice to demonstrate real-world open-source agent systems without dependency on commercial APIs.

---

## 🧠 Key Concepts Demonstrated

- **Agentic AI Architecture** - Agent-based decision making and planning
- **LangGraph State Machines** - Structured workflow orchestration
- **Tool Orchestration** - Seamless integration of Calendar, Email, and Memory tools
- **RAG (Retrieval-Augmented Generation)** - Context-aware information retrieval
- **Long-term Memory** - Persistent storage using ChromaDB
- **Open-source LLM Integration** - Ollama local model execution
- **Real API Integration** - Google Calendar & Gmail APIs
- **Streamlit Frontend** - Modern, interactive user interface

---

## 🏗️ Project Architecture

```
personal_ai_os/
├── src/
│   ├── graph.py                 # LangGraph workflow
│   ├── state.py                 # Agent state definition
│   ├── llm.py                   # Local LLM (Ollama) wrapper
│   ├── config.py                # Global configuration
│   ├── tools.py                 # Tool helpers
│   │
│   ├── nodes/                   # Agent decision nodes
│   │   ├── router.py            # Route requests to appropriate handler
│   │   ├── plan_tasks.py        # Task planning and decomposition
│   │   ├── calendar_action.py   # Calendar operations
│   │   ├── send_email.py        # Email composition and sending
│   │   ├── recall_memory.py     # Retrieve stored information
│   │   ├── save_memory.py       # Store new information
│   │   └── conversation.py      # Natural dialogue handling
│   │
│   └── memory/                  # Long-term memory (RAG)
│       ├── embeddings.py        # Embedding generation
│       └── vectorstore.py       # Vector database management
│
├── ui.py                        # Streamlit frontend application
├── main.py                      # CLI entry point
├── data/                        # ChromaDB persistence layer
├── credentials.json             # Google OAuth credentials (⚠️ not committed)
├── .gitignore
├── pyproject.toml
├── .python-version
└── README.md
```

---

## ⚙️ Tech Stack

- **Python 3.12** - Core language
- **LangGraph** - Workflow orchestration
- **LangChain** - LLM framework and tool integration
- **Ollama** - Local LLM runtime
- **ChromaDB** - Vector database for RAG
- **Google APIs** - Calendar and Gmail integration
- **Streamlit** - Web UI framework

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Ollama installed and running locally
- Google API credentials (OAuth 2.0)

### Installation

```bash
git clone https://github.com/KANDI-KANDI-ANAND/Personal_ai_os.git
cd Personal_ai_os
pip install -r requirements.txt
```

### Configuration

1. **Set up Google OAuth**
   - Download `credentials.json` from Google Cloud Console
   - Place it in the project root

2. **Configure Ollama**
   - Ensure Ollama is running: `ollama serve`
   - Verify model availability: `ollama list`

3. **Start the application**
   ```bash
   streamlit run ui.py
   ```

---

## 🔐 Important Security Note

The following files **MUST NOT** be committed to GitHub:

- `credentials.json`
- `token.json`
- `.venv/`
- `data/chroma_db/`

They are already included in `.gitignore`.

---

## 🛠️ Setup Instructions (Step-by-Step)

### 1️⃣ Install Ollama

Download & install Ollama:
[https://ollama.com](https://ollama.com)

Pull a model:

```bash
ollama pull Llama
ollama pull nomic-embed-text
```

### 2️⃣ Clone the Repository

```bash
git clone https://github.com/KANDI-KANDI-ANAND/Personal_ai_os.git
cd personal_ai_os
```

### 3️⃣ Install uv

```bash
pip install uv
```

### 4️⃣ Create Virtual Environment

```bash
uv venv
```

Activate it:

**Windows:**
```bash
.venv\Scripts\activate
```

**Mac/Linux:**
```bash
source .venv/bin/activate
```

### 5️⃣ Install Dependencies

```bash
uv pip install -r pyproject.toml
```

Or alternatively:
```bash
uv sync
```

### 6️⃣ Google API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Enable:
   - Google Calendar API
   - Gmail API
3. Create OAuth Client ID
4. Download credentials as `credentials.json`
5. Place it in the project root

퉪 **On first run, browser auth will open and create `token.json`.**

---

## ▶️ Running the Project

### CLI Mode

```bash
uv run main.py
```

### UI Mode (Streamlit)

```bash
streamlit run ui.py
```

---

## 📚 Learn More

To understand the implementation details:

- Check the **graph** for workflow logic
- Review the **state** for data structure
- Examine **tool orchestration** for API integration patterns

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

---

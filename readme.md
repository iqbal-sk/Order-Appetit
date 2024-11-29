# Order Appetit Analytics Chatbot

A conversational AI system that enables non-technical stakeholders to query MongoDB databases using natural language, powered by LLMs and multi-agent architecture.

## Overview

The Order Appetit Analytics Chatbot transforms complex MongoDB data into actionable insights through an intuitive chat interface. The system uses advanced AI techniques including Retrieval-Augmented Generation (RAG) and a multi-agent system to standardize product names, analyze schemas, and generate optimized queries.

## Features

- Natural language querying of MongoDB databases
- Multi-agent system for intelligent query processing
- Product name standardization using RAG
- Real-time schema analysis and optimization
- Intuitive Streamlit-based user interface

## Installation

```bash
git clone https://github.com/iqbal-sk/Order-Appetit.git
cd Order-Appetit
```

## Environment Setup

Create a `.env` file in the Order-Appetit/dashboard directory with the following credentials:

```plaintext
PINECONE_API_KEY="your_pinecone_key"
OPENAI_API_KEY="your_openai_key"
mongodb_uri="your_mongodb_uri"
LANGCHAIN_API_KEY="your_langchain_key"
LANGCHAIN_PROJECT="your_project_name"
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
database_name="your_database_name"
```

## Usage

### Using Docker (Recommended)

1. **Build the Docker Image**:
```bash
docker-compose build
```

2. **Run the Container**:
```bash
docker run -p 8501:8501 order-appetit-dashboard:latest
```

3. **Access the Application**:
- Open your browser and navigate to `http://localhost:8501`

### Running Locally

If you prefer to run without Docker:
```bash
streamlit run conversational_chatbot.py
```

### Query Examples
- "Show top-selling items across all restaurants"
- "Which restaurants had the highest revenue growth in the past three months?"
- "Display order volume trends by zip code"

## System Architecture

The system consists of three core agents:

**Schema Analyzer Agent**
- Maps user queries to database schemas
- Resolves product name inconsistencies
- Optimizes schema usage

**Query Builder Agent**
- Generates optimized MongoDB queries
- Validates query syntax
- Ensures efficient execution

**Data Analyst Agent**
- Executes queries and formats results
- Presents data in structured format
- Maintains naming consistency

## Project Structure

```
📁 dashboard/
├── 📁 callbacks/               # Callback handlers for agents and tasks
│   ├── agent_callbacks.py
│   └── task_callbacks.py
├── 📁 config/                 # Configuration files
│   ├── agents.yaml           # Agent definitions
│   ├── tasks.yaml           # Task definitions
│   └── schema.yaml          # Schema configurations
├── 📁 memory/                # Conversation memory management
│   └── conversation.py      # Conversation state handling
├── 📁 pipelines/            # Data processing pipelines
│   ├── data_pipeline.py
│   └── vector_db_pipeline.py
├── 📁 schemas/              # MongoDB collection schemas
│   ├── orders_schema.json
│   ├── products_schema.json
│   └── stores_schema.json
├── 📁 steps/                # Pipeline processing steps
│   ├── mongodb_products.py
│   ├── process_products.py
│   └── product_embeddings.py
├── 📁 tools/                # Utility tools for agents
│   ├── items_finder.py
│   ├── mongodb_tools.py
│   └── schema_analysis.py
├── 📁 ui/                   # Streamlit UI components
│   ├── chat_interface.py
│   ├── css.py
│   └── sidebar.py
├── 📁 utils/               # Helper utilities
│   ├── chat_utils.py
│   ├── crew_utils.py
│   └── utils.py
└── 📁 images/              # UI assets
    ├── background.png
    └── logo.png
```
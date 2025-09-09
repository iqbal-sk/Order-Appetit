# AppetiQ — Order Appetit Analytics Chatbot (Prototype)

An AI-powered analytics assistant that lets business users ask questions about Order Appetit’s MongoDB data in plain English and get precise, tabular insights — no SQL or BI tool required.

This prototype evolved into a production-grade solution. It demonstrates end‑to‑end problem solving: multi‑agent orchestration, schema understanding, query generation, execution, and presentation in a clean Streamlit UX.

## What It Does

- Conversationally answers questions about sales, products, and restaurants using MongoDB data.
- Classifies intent and routes between general chat and task‑specific data analysis.
- Analyzes schemas, resolves naming inconsistencies (e.g., “Mac n Cheese” vs “Mac & Cheese”), and builds optimized MongoDB pipelines.
- Executes queries safely, then formats results into readable, granular tables.
- Persists conversation context with short‑term memory for better follow‑ups.

## Why It Stands Out

- Product thinking: focuses on business KPIs/end‑users, not just LLM demos.
- Solid architecture: CrewAI multi‑agent system + LangChain tools + Streamlit UX.
- Practical retrieval: OpenAI embeddings + Pinecone index for item name normalization.
- Data rigor: schema‑aware analysis, query optimization, JSON‑first outputs.
- Shipping mindset: Dockerized, .env‑driven config, clean modular code, clear roadmap.

## Core Features

- Natural‑language analytics on MongoDB collections
- Multi‑agent CrewAI pipeline (Schema Analyzer, Query Builder, Data Analyst)
- Local schema loading for low‑latency analysis and consistency
- Item name normalization via embeddings + Pinecone lookup
- Streamlit chat UI with conversation threads and lightweight memory

## Tech Stack

- Backend: Python 3.12, CrewAI, LangChain, Pydantic
- LLMs/Embeddings: OpenAI (Chat + Embeddings)
- Vector DB: Pinecone
- Data: MongoDB (via PyMongo), ZenML pipelines
- UI: Streamlit
- Containerization: Docker, docker‑compose

## Architecture

- Conversational router: classifies queries as General vs Task‑Specific.
- CrewAI agents:
  - Schema Analyzer: loads schemas, identifies collections/fields, handles naming variance.
  - Query Builder: generates optimized aggregation pipelines and Python code to execute.
  - Data Analyst: validates/executes code, returns structured tables only.
- Tools: MongoDB schema analyzer, local schema reader, Python REPL executor, Pinecone‑backed item matcher.
- Memory: sliding window buffer for concise, useful context carry‑over.

## Getting Started

- Clone: `git clone https://github.com/iqbal-sk/Order-Appetit.git && cd Order-Appetit`
- Python: 3.12 recommended (Docker path below is easiest)

### Environment Variables

Create a `.env` file at repo root or export via your shell. Minimum required:

- `OPENAI_API_KEY`: OpenAI API key
- `PINECONE_API_KEY`: Pinecone API key (for item equivalence)
- `mongodb_uri`: MongoDB URI
- `database_name`: Target database name
- Optional LangSmith/telemetry: `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`, `LANGCHAIN_ENDPOINT`

### Run with Docker (recommended)

- Build + start: `docker compose up --build`
- App: open `http://localhost:8501`

Notes:
- The container runs Streamlit from `dashboard/src/dashboard/conversational_chatbot.py`.
- The code also contains an alternate agent setup in `chatbot.py`; the Flow‑based version is default.

### Run locally (without Docker)

- Install deps: `pip install -r requirements.txt && pip install crewai~=0.76.9 crewai-tools~=0.13.4`
- Start UI: `cd dashboard/src/dashboard && streamlit run conversational_chatbot.py`

## Usage Examples

- “Give sales of biryani till now.”
- “Which month has the highest sales of pasta?”
- “Top 10 restaurants by sales in the last 12 months.”
- “What are the sales of mac n cheese for the last 7 months?”

## Configuration

- Agents/tasks: `dashboard/src/dashboard/config/agents.yaml`, `dashboard/src/dashboard/config/tasks.yaml`
- Schemas mapping: `dashboard/src/dashboard/config/schema.yaml`
- Local schema JSONs: `dashboard/src/dashboard/schemas/*.json`

You can tailor agent goals/instructions for your data domain and tighten/relax the Data Analyst’s behavior to be “table‑only, no commentary”.

## Pipelines (Embeddings + Pinecone)

- Product normalization uses embeddings to find semantically similar item names.
- ZenML pipelines:
  - `product_data_pipeline`: fetch → clean/standardize products from MongoDB.
  - `product_embedding_pipeline`: generate OpenAI embeddings → upsert into Pinecone.
- Steps live in `dashboard/src/dashboard/steps/*` and `dashboard/src/dashboard/pipelines/*`.

Run the embedding pipeline after setting env vars to populate the Pinecone index used by the chatbot’s item‑matching tool.

## Project Structure

```
dashboard/
  src/dashboard/
    callbacks/           # Agent/Task progress to UI
    config/              # Agents, tasks, schema configs
    memory/              # ConversationBufferWindow
    pipelines/           # ZenML pipelines
    schemas/             # Local schema JSONs
    steps/               # ZenML steps (Mongo, embeddings, Pinecone)
    tools/               # Mongo analyzer, item finder, Python executor
    ui/                  # Streamlit chat + sidebar + CSS
    utils/               # Crew assembly, summarizers, chat state helpers
    chatbot.py           # Alt crew setup (legacy)
    conversational_chatbot.py  # Flow + router entrypoint
```


## Limitations & Next Steps

- Limitations:
  - No charts/visualizations yet (tables only)
  - Follow‑up query understanding can be improved further
  - Some latency on first‑run model/tools initialization
- Roadmap:
  - Add plotly/altair‑based charts and CSV export
  - Query caching and results persistence
  - Role‑based access control + audit logs
  - Observability (LangSmith) and eval harness
  - Expand semantic normalization beyond products (e.g., restaurant names, categories)

## Security Notes

- Keep secrets in `.env` or your secrets manager; never commit keys.
- Pipelines read‑only where possible; writing to Pinecone is scoped to the configured index.
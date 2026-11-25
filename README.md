# LYFTR AI Chatbot

A full-stack, AI-powered chatbot built with React, FastAPI, LiteLLM, and SQLite. The application supports multi-turn conversations, automatic API key failover, response caching, per-request token tracking, and Docker-based deployment.

## 1. Live URLs

- **Frontend:** https://lyftr-ai-chatbot-lovat.vercel.app
- **Backend:** https://lyftr-ai-chatbot-production-8b00cc21.up.railway.app
- **API Documentation:** https://lyftr-ai-chatbot-production-8b00cc21.up.railway.app/docs
- **Health Endpoint:** https://lyftr-ai-chatbot-production-8b00cc21.up.railway.app/health
- **GitHub Repository:** [Insert your public GitHub repository URL]

**Technology stack**

- Frontend: React, Vite, JavaScript, CSS
- Backend: Python, FastAPI, Pydantic, SQLAlchemy
- LLM integration: LiteLLM with Google Gemini
- Database: SQLite
- Containerization: Docker, Docker Compose
- Deployment: Vercel (frontend), Railway (backend)

## 2. Run locally: with Docker and without

### Prerequisites

- Python 3.11 or compatible version
- Node.js and npm
- Docker Desktop and Docker Compose
- At least two working LLM API keys
- Make, for the required Makefile commands

### Environment configuration

Create `backend/.env` using the provided `.env.example` as a reference.

```env
LLM_API_KEYS=YOUR_FIRST_API_KEY,YOUR_SECOND_API_KEY
LLM_MODEL=gemini/gemini-3.5-flash-lite
DATABASE_URL=sqlite:///./app.db
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
ENABLE_FAILURE_SIMULATION=true
```

Never commit real API keys.

### Running with Docker

From the repository root:

```bash
make up
```

Alternatively:

```bash
docker compose up --build -d
```

Services:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API documentation: http://localhost:8000/docs

Stop the services:

```bash
make down
```

Docker Compose mounts a named volume at `/data`, with the SQLite database stored at `/data/app.db`.

### Running without Docker

Start the backend:

```bash
cd backend
python -m venv .venv
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Activate the virtual environment before installing dependencies if preferred.

In a separate terminal, start the frontend:

```bash
cd frontend
npm install
npm run dev
```

Configure `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### Running backend tests

```bash
cd backend
python -m pytest tests -v
```

## 3. Design decisions: key fallback, caching, SQLite session storage

### API architecture

The frontend communicates with FastAPI through JSON-based HTTP requests.

The backend exposes three application endpoints:

- `GET /health`
- `POST /chat`
- `GET /sessions/{session_id}/messages`

FastAPI validates incoming requests using Pydantic.

### Multi-turn conversation memory

Each conversation is identified by a client-generated `session_id`.

Messages are stored in SQLite and retrieved in chronological order. Before each LLM request, the backend constructs a message list containing the system prompt, previous conversation history, and the latest user message.

Successful user and assistant messages are saved together. Failed inference requests are not added to conversation history.

### API key failover

The backend maintains a pool of API keys loaded from environment variables.

When a provider returns a supported retryable error, such as HTTP 429 or a server-side failure, the backend attempts another configured key.

The response metadata identifies the successful key and the number of failed attempts without exposing actual credentials.

When all providers are unavailable, the backend returns HTTP 503 with a JSON error response.

### LiteLLM response caching

LiteLLM's built-in in-memory cache is used to reuse responses for matching requests.

Caching reduces repeated inference calls and improves response latency.

The API distinguishes between:

- `LIVE_INFERENCE`: a response generated through the model provider.
- `LLM_CACHE`: a response retrieved from LiteLLM's cache.

Cached responses preserve the original reply and token usage while reporting a null `key_id`.

### SQLite persistence

SQLite stores conversation history without requiring an external database service.

The database schema is created automatically during application startup.

For Docker deployment, the database file is configured through `DATABASE_URL` and stored under `/data` using a named volume.

### Token usage and latency

Every successful assistant response includes:

- Model name
- Resolution source
- Server-measured latency in milliseconds
- Input tokens for that request
- Output tokens for that request
- Successful key identifier or null
- Number of fallback attempts

Token usage is reported per request rather than as a conversation-wide total.

## 4. Verification: how to see failover, cache hits and per-message token usage

### Health check

```http
GET /health
```

Expected response with two configured keys:

```json
{
  "status": "ok",
  "keys_configured": 2,
  "cache_enabled": true
}
```

### Cache verification

Send the same initial message in two different new sessions using the same model and system prompt.

The first request should return `LIVE_INFERENCE`, and the second should return `LLM_CACHE`.

The cached reply and token usage should match the original response, with lower latency.

### Failover verification

Use the `X-Simulate-Failure` header:

| Header | Expected behavior |
|---|---|
| `key_1=429` | Retry using key 2 |
| `key_1=500` | Retry using key 2 |
| `key_1=429,key_2=500` | HTTP 503 |
| `*=429` | HTTP 503 |

Failure simulation is enabled only when `ENABLE_FAILURE_SIMULATION=true`.

### Conversation history

```http
GET /sessions/{session_id}/messages
```

Returns stored user and assistant messages in chronological order, including metadata for assistant messages.

Unknown sessions return HTTP 404.

### Validation

Invalid chat requests, including missing required fields, empty messages, and messages exceeding 4000 characters after trimming, return HTTP 422.

### Frontend verification

Each assistant message displays its response source, model, latency, input tokens, and output tokens.

The frontend displays readable error messages and generates a new session on each page load.

## 5. Setup Used: your editor and AI tools

- **Development environment:** Visual Studio Code, PowerShell, Git and GitHub
- **Backend development:** Python, FastAPI and SQLite
- **Frontend development:** React and Vite
- **API testing:** FastAPI Swagger UI and pytest
- **Containerization:** Docker Desktop and Docker Compose
- **Deployment:** Railway and Vercel
- **AI assistance:** ChatGPT was used for implementation guidance, debugging, architecture explanations, and documentation assistance.

The application was developed and verified incrementally through local tests, Docker execution, and public deployment.

## 6. Bonus features (if any)

An optional system-prompt field allows users to customize assistant behavior for their session.

The frontend also includes a responsive chat layout, loading feedback, and readable API error messages.

The main implementation prioritizes the mandatory API contract, resilience, caching accuracy, persistence, and deployment requirements.
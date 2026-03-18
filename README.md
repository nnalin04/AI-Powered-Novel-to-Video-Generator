# AI Film Studio (Vertex AI Edition)

An autonomous agentic workflow for converting stories into animated episodes using Google Vertex AI (Gemini 2.5 Pro, Imagen 3, Veo).

## 🏗 Architecture

The system uses **LangGraph** to orchestrate a pipeline of specialized agents:

1.  **Story Analyst**: Extracts plot & characters (Gemini 2.5 Pro).
2.  **Scriptwriter**: Writes screenplay & scene breakdown.
3.  **Character Designer**: Generates assets (Imagen 3 / Nano Banana).
4.  **Director**: Creates storyboards.
5.  **Animator**: Generates video clips (Google Veo).
6.  **Audio Engineer**: Generates TTS (Google Cloud TTS).
7.  **Editor**: Assembles the final video.
8.  **Critic**: Quality Assurance.

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- Google Cloud Service Account JSON (with Vertex AI & TTS specific permissions)

### Configuration

1.  Copy `.env.example` to `.env`.
2.  Set `GOOGLE_APPLICATION_CREDENTIALS` to the path of your JSON key file (mapped into Docker).
3.  Set your desired model defaults (Pre-configured for Google).

### Running the Studio

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.

### Generating an Episode

Send a POST request to trigger the pipeline:

```bash
curl -X POST "http://localhost:8000/generate/episode" \
     -H "Content-Type: application/json" \
     -d '{"story_text": "A futuristic detective story in Neo-Tokyo..."}'
```

## 🛠 Project Structure

- `ai_film_studio/agents`: Agent logic.
- `ai_film_studio/core`: State definitions & interfaces.
- `ai_film_studio/providers`: Google Vertex AI adapters.
- `ai_film_studio/web`: FastAPI backend.

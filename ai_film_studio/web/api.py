import uuid
from fastapi import FastAPI, BackgroundTasks, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from ai_film_studio.core.workflow import app_graph
from ai_film_studio.core.state import EpisodeState

app = FastAPI(title="AI Film Studio API")

# Mount Static & Templates
app.mount("/static", StaticFiles(directory="ai_film_studio/web/static"), name="static")
templates = Jinja2Templates(directory="ai_film_studio/web/templates")

class GenerateRequest(BaseModel):
    story_text: str

@app.get("/")
async def read_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate/episode")
async def generate_episode(request: GenerateRequest, background_tasks: BackgroundTasks):
    """Starts the generation process asynchronously."""
    story_text = request.story_text
    job_id = str(uuid.uuid4())
    
    # Initialize State
    initial_state = EpisodeState(
        project_id=job_id,
        episode_number=1,
        raw_story_input=story_text
    )
    
    # In a real app, we'd kick off a Celery task or background thread
    # For MVP verification, we might just run it (blocking) or use background_tasks
    background_tasks.add_task(run_pipeline, initial_state)
    
    return {"job_id": job_id, "status": "queued"}

async def run_pipeline(state: EpisodeState):
    """Runs the LangGraph workflow."""
    try:
        print(f"Starting Pipeline for Job {state.project_id}", flush=True)
        async for output in app_graph.astream(state):
            # In a real app, we'd push updates to Redis/WebSockets here
            for key, value in output.items():
                print(f"Node '{key}' finished.", flush=True)
        print(f"Pipeline Finished for Job {state.project_id}", flush=True)
    except Exception as e:
        print(f"PIPELINE CRITICAL ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()

# Simple WebSocket for real-time (Placeholder)
@app.websocket("/ws/status/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await websocket.accept()
    await websocket.send_text(f"Connected to status stream for {job_id}")

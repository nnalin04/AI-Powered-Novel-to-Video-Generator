print("DEBUG: Script started", flush=True)
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/nishitnalinsrivastava/dev/AI Agent/AI-Powered Novel-to-Video Generator/secrets/vertex-service-key.json"

print("DEBUG: Importing asyncio", flush=True)
import asyncio
print("DEBUG: Importing uuid", flush=True)
import uuid
print("DEBUG: Importing EpisodeState", flush=True)
from ai_film_studio.core.state import EpisodeState
print("DEBUG: Importing app_graph", flush=True)
from ai_film_studio.core.workflow import app_graph
print("DEBUG: All imports done", flush=True)

async def main():
    job_id = str(uuid.uuid4())
    state = EpisodeState(
        project_id=job_id,
        episode_number=1,
        raw_story_input="A small robot discovers a flower in a wasteland."
    )
    
    print(f"--- Simulating Pipeline for {job_id} ---", flush=True)
    try:
        async for output in app_graph.astream(state):
            for key, value in output.items():
                print(f"Node '{key}' finished.", flush=True)
    except Exception as e:
        print(f"PIPELINE CRITICAL ERROR: {e}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())

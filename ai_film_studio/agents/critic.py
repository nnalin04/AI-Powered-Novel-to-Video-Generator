from typing import Dict, Any
from ai_film_studio.core.state import EpisodeState
from ai_film_studio.config.settings import settings

async def critic_node(state: EpisodeState) -> Dict[str, Any]:
    print("--- CRITIC AGENT (QA) STARTED ---")
    
    if not settings.ENABLE_CRITIC_LOOPS:
        print("Critic loops disabled by config. Skipping.")
        return {}

    errors = []
    
    # 1. Structural Validation
    if not state.screenplay:
        errors.append("Critical: No Screenplay generated.")
    
    if not state.scenes:
        errors.append("Critical: No Scenes parsed.")
        
    # 2. visual Validation (Consistency Check Mock)
    if settings.ENFORCE_CONSISTENCY_CHECKS:
        missing_chars = [name for name, p in state.characters.items() if not p.image_paths]
        if missing_chars:
             errors.append(f"Consistency Error: Characters {missing_chars} have no reference images.")

    # 3. Output Validation
    if not state.final_video_path:
        errors.append("Critical: Final Video path is missing.")

    if errors:
        print(f"QA FAILED with errors: {errors}")
        # In a real graph, we might return a 'retry' command or specific node routing
        return {"errors": errors}
    else:
        print("QA PASSED. Episode ready for broadcast.")
        return {}

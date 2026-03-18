from typing import Dict, Any, List
from ai_film_studio.core.state import EpisodeState, Scene
from ai_film_studio.providers.factory import ProviderFactory

async def scriptwriter_node(state: EpisodeState) -> Dict[str, Any]:
    print("--- SCRIPTWRITER AGENT STARTED ---", flush=True)
    
    llm = ProviderFactory.get_llm()
    
    # 1. Generate Screenplay
    screenplay_prompt = f"""
    You are an expert Screenwriter.
    Based on the following story analysis, write a detailed screenplay for an animated episode (approx 5 minutes).
    Include dialogue, action lines, and scene headers.
    
    Story Analysis: {state.story_analysis}
    """
    
    screenplay_text = await llm.generate_text("You are a professional Screenwriter.", screenplay_prompt)
    
    # 2. Parse Scenes structured data
    # In a real app we'd chain this or use function calling
    scene_parsing_prompt = f"""
    Given the screenplay below, extract a list of scenes with the following fields:
    - sequence_order
    - visual_description (for image gen)
    - characters_present (list of names)
    - dialogue (list of dicts with 'speaker' and 'text')
    - estimated_duration (float, in seconds)
    
    Screenplay:
    {screenplay_text}
    """
    
    schema = "JSON with key 'scenes': list of objects matching the Scene model structure."
    
    scenes_data = await llm.generate_json("You are a Data Extraction Specialist.", scene_parsing_prompt, schema=schema)
    
    # Convert to Pydantic models
    # Note: Validation might fail if LLM output is imperfect. MVP handles this loosely.
    scenes_list = []
    for idx, s in enumerate(scenes_data.get('scenes', [])):
        # Ensure ID and sequence are set
        s['id'] = s.get('id', idx + 1)
        s['sequence_order'] = s.get('sequence_order', idx + 1)
        s['script_content'] = s.get('script_content', "...") 
        s['estimated_duration'] = float(s.get('estimated_duration', 10.0)) # Default to 10s if missing
        
        # Basic validation/cleaning could happen here
        scenes_list.append(Scene(**s))
        
    return {
        "screenplay": screenplay_text,
        "scenes": scenes_list
    }

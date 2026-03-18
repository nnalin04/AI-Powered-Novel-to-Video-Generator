import asyncio
from typing import Dict, Any
from ai_film_studio.core.state import EpisodeState
from ai_film_studio.providers.factory import ProviderFactory

async def director_node(state: EpisodeState) -> Dict[str, Any]:
    print("--- DIRECTOR (STORYBOARD) AGENT STARTED ---")
    
    image_gen = ProviderFactory.get_image_gen()
    updated_scenes = []
    
    # Parallel generation of visual concepts for scenes
    tasks = []
    
    for scene in state.scenes:
        # Create a rich visual prompt
        # In a real system, we'd inject character embeddings/references here
        prompt = f"""
        Cinematic Storyboard.
        Scene ID: {scene.id}
        Action: {scene.visual_description}
        Setting: {scene.script_content[:100]}...
        Style: Anime, High quality, Broadcast ready.
        """
        
        async def gen_scene_visual(s=scene, p=prompt):
            # Generate the 'keyframe' or storyboard for the scene
            path = await image_gen.generate_image(p)
            s.visual_description = f"{s.visual_description} [Ref: {path}]"
            # In a real app, we might store the path in a dedicated field or the 'video_clip_path' temporarily
            # For now, let's assume valid generation implies we are ready for animation.
            return s
            
        tasks.append(gen_scene_visual())
        
    updated_scenes = await asyncio.gather(*tasks)
    
    return {"scenes": updated_scenes}

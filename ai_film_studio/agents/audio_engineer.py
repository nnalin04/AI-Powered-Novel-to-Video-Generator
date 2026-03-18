import asyncio
from typing import Dict, Any
from ai_film_studio.core.state import EpisodeState
from ai_film_studio.providers.factory import ProviderFactory

async def audio_engineer_node(state: EpisodeState) -> Dict[str, Any]:
    print("--- AUDIO ENGINEER AGENT STARTED ---")
    
    tts_provider = ProviderFactory.get_audio()
    updated_scenes = []
    
    tasks = []

    for scene in state.scenes:
        # If there's dialogue, generate audio
        if scene.dialogue:
            # For MVP, we just concatenate all dialogue into one audio file for the scene
            # In a real app, we'd handle timing per line and separate files
            
            full_text = " ".join([d.get('text', '') for d in scene.dialogue])
            
            # Simple voice logic: pick a voice based on speaker gender if known, or default
            # Here we just use default
            voice_id = "en-US-Journey-F" # Example Google Voice
            
            async def gen_audio_task(s=scene, t=full_text, v=voice_id):
                path = await tts_provider.generate_speech(t, v)
                s.audio_track_path = path
                return s
            
            tasks.append(gen_audio_task())
        else:
            # No dialogue, keep scene as is
            tasks.append(asyncio.sleep(0, result=scene))

    # Wait for all TTS generation
    updated_scenes_raw = await asyncio.gather(*tasks)
    
    # asyncio.gather returns the results in order, but dealing withmixed types (Scene vs sleep result)
    # The sleep helper above returns the scene object so it's consistent.
    updated_scenes = list(updated_scenes_raw)

    return {"scenes": updated_scenes}

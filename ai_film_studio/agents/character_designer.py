import asyncio
from typing import Dict, Any, List
from ai_film_studio.core.state import EpisodeState, CharacterProfile
from ai_film_studio.providers.factory import ProviderFactory
from ai_film_studio.core.memory import memory_store

async def character_designer_node(state: EpisodeState) -> Dict[str, Any]:
    print("--- CHARACTER DESIGNER AGENT STARTED ---")
    
    image_gen = ProviderFactory.get_image_gen()
    
    # We iterate over the characters found by the Story Analyst
    # state.characters is a Dict[str, CharacterProfile]
    
    # If using story analysis output directly:
    raw_characters = state.story_analysis.get('characters', [])
    updated_characters = state.characters.copy()
    
    generation_tasks = []
    
    for char_data in raw_characters:
        name = char_data.get('name', 'Unknown')
        desc = char_data.get('visual_description', '')
        
        # Enforce consistency check (Risk Protocol)
        # 1. Search Memory
        existing_assets = await memory_store.search_assets(name, asset_type="character", limit=1)
        ref_image = None
        if existing_assets and existing_assets[0]['distance'] < 0.2: # Threshold
             print(f"Found existing character: {existing_assets[0]['name']}")
             ref_image = existing_assets[0]['metadata'].get('image_path')
        
        prompt = f"Character Design Sheet: {name}. {desc}. High quality, white background, multiple angles."
        if ref_image:
             prompt += f" Maintain consistency with previous design (reference provided to model)."
             
        # Async generation
        async def gen_task(n=name, c_desc=desc, p=prompt, ref=ref_image):
            path = await image_gen.generate_image(p, reference_images=[ref] if ref else None)
            
            # Save new asset to memory for next time
            await memory_store.add_asset(
                name=n,
                asset_type="character",
                metadata={"image_path": path, "description": c_desc},
                context_text=f"{n} {c_desc}"
            )
            
            return n, CharacterProfile(
                name=n,
                description=c_desc,
                visual_spec={'raw': c_desc},
                image_paths=[path]
            )
            
        generation_tasks.append(gen_task())
    
    # Run all character generations in parallel
    results = await asyncio.gather(*generation_tasks)
    
    for name, profile in results:
        updated_characters[name] = profile
        
    return {"characters": updated_characters}

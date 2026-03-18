from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from ai_film_studio.core.state import EpisodeState
from ai_film_studio.providers.factory import ProviderFactory
from ai_film_studio.core.memory import memory_store

async def story_analyst_node(state: EpisodeState) -> Dict[str, Any]:
    print("--- STORY ANALYST AGENT STARTED ---", flush=True)
    
    # 1. Get LLM
    llm = ProviderFactory.get_llm()
    
    # 2. Define Prompts (Simplistic for MVP)
    system_prompt = """
    You are an expert Story Analyst for an AI Film Studio.
    Your job is to analyze raw story input and extract:
    1. A concise plot summary.
    2. A list of key characters with visual descriptions.
    3. A breakdown of the story into linear scenes.
    
    Output structured JSON data.
    """
    
    user_prompt = f"""
    Analyze this story:
    {state.raw_story_input}
    """
    
    # 2b. (NEW) Retrieve Context (RAG)
    try:
        # Search for similar past themes or summaries
        past_hits = await memory_store.search_assets(state.raw_story_input[:200], asset_type="episode_summary")
        if past_hits:
            context = "\n".join([f"- Previous Episode Context: {h['metadata'].get('summary')} (Distance: {h['distance']:.2f})" for h in past_hits])
            user_prompt += f"\n\nContext from previous episodes:\n{context}"
            print("--- RAG: Injected Context from Memory ---", flush=True)
    except Exception as e:
        print(f"RAG Warning: {e}", flush=True)
    
    # 3. Define Output Schema (Implicitly required by generate_json)
    # In a full LangChain implementation we might use PydanticOutputParser
    schema_desc = "JSON with keys: plot_summary, characters (list), scenes (list)"
    
    # 4. Call Model
    try:
        analysis_result = await llm.generate_json(system_prompt, user_prompt, schema=schema_desc)
        
        # 5. Return updates to state
        # 6. (NEW) Store this analysis in memory
        try:
             summary = analysis_result.get('plot_summary', '')
             if summary:
                 await memory_store.add_asset(
                     name=f"Episode {state.episode_number} Summary",
                     asset_type="episode_summary",
                     metadata={"summary": summary, "project_id": state.project_id},
                     context_text=summary
                 )
        except Exception as e:
            print(f"Memory Write Warning: {e}", flush=True)

        return {"story_analysis": analysis_result}
        
    except Exception as e:
        print(f"Error in Story Analyst: {e}", flush=True)
        return {"errors": [str(e)]}

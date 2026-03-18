from langgraph.graph import StateGraph, END
from ai_film_studio.core.state import EpisodeState
from ai_film_studio.agents.story_analyst import story_analyst_node
from ai_film_studio.agents.scriptwriter import scriptwriter_node
from ai_film_studio.agents.character_designer import character_designer_node
from ai_film_studio.agents.director import director_node
from ai_film_studio.agents.animator import animator_node

from ai_film_studio.agents.audio_engineer import audio_engineer_node
from ai_film_studio.agents.editor import editor_node
from ai_film_studio.agents.critic import critic_node

# Define Graph
workflow = StateGraph(EpisodeState)

# Add Nodes
workflow.add_node("story_analyst", story_analyst_node)
workflow.add_node("scriptwriter", scriptwriter_node)
workflow.add_node("character_designer", character_designer_node)
workflow.add_node("director", director_node)
workflow.add_node("animator", animator_node)
workflow.add_node("audio_engineer", audio_engineer_node)
workflow.add_node("editor", editor_node)
workflow.add_node("critic", critic_node)

# Define Edges
workflow.set_entry_point("story_analyst")
workflow.add_edge("story_analyst", "scriptwriter")
workflow.add_edge("scriptwriter", "character_designer")
workflow.add_edge("character_designer", "director")
workflow.add_edge("director", "animator")
workflow.add_edge("animator", "audio_engineer") # Sequential for simplicity
workflow.add_edge("audio_engineer", "editor")
workflow.add_edge("editor", "critic")
workflow.add_edge("critic", END)

# Compile
app_graph = workflow.compile()

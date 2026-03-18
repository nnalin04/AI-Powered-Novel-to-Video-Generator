from typing import List, Dict, Optional, Annotated
from pydantic import BaseModel, Field
import operator

# --- Data Models ---

class CharacterProfile(BaseModel):
    name: str
    description: str
    visual_spec: Dict[str, str] = Field(default_factory=dict) # Hair, eyes, clothing key-values
    voice_profile: Dict[str, str] = Field(default_factory=dict) # Pitch, accent, provider_id
    image_paths: List[str] = Field(default_factory=list) # Local or S3 paths to reference images
    consistency_embedding_id: Optional[str] = None # Vector DB ID

class Scene(BaseModel):
    id: int
    sequence_order: int
    script_content: str
    visual_description: str
    characters_present: List[str]
    dialogue: List[Dict[str, str]] # [{'speaker': 'Hero', 'text': 'Hello'}]
    estimated_duration: float
    status: str = "pending" # pending, generating, done, failed
    video_clip_path: Optional[str] = None
    audio_track_path: Optional[str] = None

# --- Graph State ---

class EpisodeState(BaseModel):
    # Metadata
    project_id: str
    episode_number: int
    
    # Narrative Inputs
    raw_story_input: str
    
    # Intermediate Artifacts
    story_analysis: Dict = Field(default_factory=dict) # Plot, themes, etc.
    screenplay: str = "" # Full text script
    
    # Core Assets
    scenes: List[Scene] = Field(default_factory=list)
    characters: Dict[str, CharacterProfile] = Field(default_factory=dict)
    
    # Final Outputs
    final_video_path: Optional[str] = None
    
    # Operational Logs (Append-only)
    errors: List[str] = Field(default_factory=list)
    quality_metrics: Dict[str, float] = Field(default_factory=dict)

    def add_error(self, error_msg: str):
        self.errors.append(error_msg)

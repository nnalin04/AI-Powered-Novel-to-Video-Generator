from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # --- API Keys ---
    OPENAI_API_KEY: Optional[str] = None
    RUNWAY_API_KEY: Optional[str] = None
    ELEVENLABS_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None # For Gemini/PaLM
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None # For Vertex AI
    REPLICATE_API_TOKEN: Optional[str] = None
    
    # --- Model Selection ---
    LLM_PROVIDER: str = "google-gemini-2.5-pro"
    IMAGE_PROVIDER: str = "replicate-flux-pro"
    FALLBACK_IMAGE_PROVIDER: str = "replicate-flux-schnell"
    VIDEO_PROVIDER: str = "replicate-hailuo"
    FALLBACK_VIDEO_PROVIDER: str = "replicate-wan"
    
    # --- Infrastructure ---
    # Memory uses embedded ChromaDB
    
    # --- Operational & Risk Protocols ---
    MAX_PARALLEL_JOBS: int = 5
    SPEED_MODE: bool = False
    
    # Strictly Enforced Defaults
    ENABLE_CRITIC_LOOPS: bool = True
    ENFORCE_CONSISTENCY_CHECKS: bool = True
    STRICT_BUDGET_LIMIT: float = 150.00
    AUTO_RETRY_ON_RATE_LIMIT: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

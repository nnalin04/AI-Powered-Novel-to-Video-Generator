from abc import ABC, abstractmethod
from typing import List, Optional, Any

class LLMProvider(ABC):
    """Abstract interface for Large Language Models."""
    @abstractmethod
    async def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        pass
    
    @abstractmethod
    async def generate_json(self, system_prompt: str, user_prompt: str, schema: Any) -> dict:
        pass

class ImageGenerationProvider(ABC):
    """Abstract interface for Image Generation."""
    @abstractmethod
    async def generate_image(self, prompt: str, negative_prompt: str = "", width: int = 1024, height: int = 1024, reference_images: Optional[List[str]] = None) -> str:
        """Returns local path or URL of generated image."""
        pass

class VideoGenerationProvider(ABC):
    """Abstract interface for Video Generation."""
    @abstractmethod
    async def generate_clip(self, prompt: str, image_url: Optional[str] = None, duration_seconds: int = 4) -> str:
        """Returns local path or URL of generated video clip."""
        pass

class AudioProvider(ABC):
    """Abstract interface for TTS/Audio."""
    @abstractmethod
    async def generate_speech(self, text: str, voice_id: str) -> str:
        """Returns local path to audio file."""
        pass

class EmbeddingProvider(ABC):
    """Abstract interface for Vector Embeddings."""
    @abstractmethod
    async def get_embedding(self, text: str) -> List[float]:
        pass

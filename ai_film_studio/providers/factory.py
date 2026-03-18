from ai_film_studio.config.settings import settings
from ai_film_studio.core.interfaces import LLMProvider, ImageGenerationProvider, VideoGenerationProvider, AudioProvider, EmbeddingProvider

# Import Concrete Implementations
from ai_film_studio.providers.llm.gemini import GeminiProvider
from ai_film_studio.providers.image.replicate_image import ReplicateImageProvider
from ai_film_studio.providers.video.replicate_video import ReplicateVideoProvider
from ai_film_studio.providers.audio.elevenlabs import ElevenLabsProvider
from ai_film_studio.providers.embedding.vertex_embedding import VertexEmbeddingProvider

class ProviderFactory:
    @staticmethod
    def get_llm() -> LLMProvider:
        if "gemini" in settings.LLM_PROVIDER:
            # Dynamic Model Selection based on SPEED_MODE
            model = "gemini-2.5-flash" if settings.SPEED_MODE else "gemini-2.5-pro"
            print(f"Factory: Initializing LLM with {model} (Speed Mode: {settings.SPEED_MODE})")
            return GeminiProvider(model_name=model)
        raise ValueError(f"Unknown LLM Provider: {settings.LLM_PROVIDER}")

    @staticmethod
    def get_image_gen() -> ImageGenerationProvider:
        if settings.SPEED_MODE or "schnell" in settings.IMAGE_PROVIDER:
             print("Factory: Using FLUX Schnell (Fast Drafts) for Speed.")
             return ReplicateImageProvider(model_name=settings.FALLBACK_IMAGE_PROVIDER)
        
        if "replicate" in settings.IMAGE_PROVIDER:
            return ReplicateImageProvider(model_name=settings.IMAGE_PROVIDER.replace("replicate-", ""))
        
        print("Factory: Unknown Image Provider. Falling back to FLUX.2 Pro.")
        return ReplicateImageProvider()

    @staticmethod
    def get_video_gen() -> VideoGenerationProvider:
        if settings.SPEED_MODE or "wan" in settings.VIDEO_PROVIDER:
             print("Factory: Using Wan 2.2 for Speed/Cost.")
             return ReplicateVideoProvider(model_name=settings.FALLBACK_VIDEO_PROVIDER.replace("replicate-", ""))
             
        if "replicate" in settings.VIDEO_PROVIDER:
            return ReplicateVideoProvider(model_name=settings.VIDEO_PROVIDER.replace("replicate-", ""))
            
        raise ValueError(f"Unknown Video Provider: {settings.VIDEO_PROVIDER}")

    @staticmethod
    def get_audio() -> AudioProvider:
        return ElevenLabsProvider()

    @staticmethod
    def get_embedding() -> EmbeddingProvider:
        return VertexEmbeddingProvider()

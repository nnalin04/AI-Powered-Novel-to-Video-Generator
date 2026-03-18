from typing import List
from google import genai
from google.genai import types
from ai_film_studio.core.interfaces import EmbeddingProvider
from ai_film_studio.config.settings import settings

class VertexEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "text-embedding-004"):
        self.model_name = model_name
        if not settings.GOOGLE_API_KEY:
             print("Warning: GOOGLE_API_KEY is not set. Embedding generation will fail.")
        
        self.client = genai.Client()

    async def get_embedding(self, text: str) -> List[float]:
        try:
            # The genai SDK supports embeddings via models.embed_content
            # The async client is available via client.aio
            response = await self.client.aio.models.embed_content(
                model=self.model_name,
                contents=text
            )
            # The response object has an embeddings list
            # Each embedding has a values list
            return response.embeddings[0].values
        except Exception as e:
            print(f"Embedding Error: {e}")
            # Return dummy embedding if generation fails to prevent total crashing in MVP
            return [0.0] * 768

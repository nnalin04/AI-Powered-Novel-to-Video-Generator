import json
from typing import Any, Dict
from google import genai
from google.genai import types
from ai_film_studio.core.interfaces import LLMProvider
from ai_film_studio.config.settings import settings

class GeminiProvider(LLMProvider):
    def __init__(self, model_name: str = "gemini-2.5-pro"):
        self.model_name = model_name
        # The new google-genai SDK uses GOOGLE_API_KEY from the environment automatically
        if not settings.GOOGLE_API_KEY:
             print("Warning: GOOGLE_API_KEY is not set. Gemini generation will fail.")
        
        # Initialize the client
        self.client = genai.Client()

    async def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        try:
            # We can use system instruction with google-genai
            config = types.GenerateContentConfig(
                temperature=temperature,
                system_instruction=system_prompt,
            )
            
            # The async client is available via client.aio
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=config
            )
            return response.text
        except Exception as e:
            print(f"Gemini Error (generate_text): {e}")
            return f"Error: {e}"

    async def generate_json(self, system_prompt: str, user_prompt: str, schema: Any) -> Dict:
        try:
            # Tell Gemini to output JSON
            config = types.GenerateContentConfig(
                temperature=0.2,
                system_instruction=system_prompt + f"\n\nOutput JSON matching this schema: {schema}",
                response_mime_type="application/json",
            )
            
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=config
            )
            
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                raise ValueError(f"Failed to parse JSON from model response: {response.text}")
        except Exception as e:
            print(f"Gemini Error (generate_json): {e}")
            return {"errors": [str(e)]}

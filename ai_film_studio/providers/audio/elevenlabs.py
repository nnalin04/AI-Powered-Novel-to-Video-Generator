import os
from elevenlabs import Voice, VoiceSettings
from elevenlabs.client import ElevenLabs
from ai_film_studio.core.interfaces import AudioProvider
from ai_film_studio.config.settings import settings

class ElevenLabsProvider(AudioProvider):
    def __init__(self):
        if not settings.ELEVENLABS_API_KEY:
            print("Warning: ELEVENLABS_API_KEY is not set. Generation will fail.")
            
        # The ElevenLabs client automatically picks up ELEVENLABS_API_KEY from environment
        self.client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)

    async def generate_speech(self, text: str, voice_id: str = "Rachel") -> str:
        try:
            print(f"Audio: Generating speech with ElevenLabs (Voice: {voice_id})")
            
            # Using the v1.0.0 synchronous generator pattern, we can consume it into a file
            audio_generator = self.client.generate(
                text=text,
                voice=voice_id,
                model="eleven_multilingual_v2" # Good default choice
            )
            
            # Ensure directory exists
            os.makedirs("assets/audio", exist_ok=True)
            filename = f"assets/audio/{hash(text)}.mp3"
            
            with open(filename, "wb") as out:
                for chunk in audio_generator:
                    if chunk:
                        out.write(chunk)
                        
            return filename
        except Exception as e:
            print(f"ElevenLabs Error: {e}")
            return "assets/placeholders/silence.mp3"

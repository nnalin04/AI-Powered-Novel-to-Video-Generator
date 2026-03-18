from google.cloud import texttospeech
from ai_film_studio.core.interfaces import AudioProvider
from ai_film_studio.config.settings import settings
import os

class GoogleTTSProvider(AudioProvider):
    def __init__(self):
        # Assumes GOOGLE_APPLICATION_CREDENTIALS is set in env
        self.client = texttospeech.TextToSpeechClient()

    async def generate_speech(self, text: str, voice_id: str = "en-US-Standard-A") -> str:
        
        input_text = texttospeech.SynthesisInput(text=text)
        
        # Simple voice selection logic for MVP
        # In a real app, mapping 'voice_id' to specific Google Voice params would be more robust
        voice_params = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=voice_id
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = self.client.synthesize_speech(
            input=input_text, voice=voice_params, audio_config=audio_config
        )

        # Ensure directory exists
        os.makedirs("assets/audio", exist_ok=True)
        filename = f"assets/audio/{hash(text)}.mp3"
        
        with open(filename, "wb") as out:
            out.write(response.audio_content)
            
        return filename

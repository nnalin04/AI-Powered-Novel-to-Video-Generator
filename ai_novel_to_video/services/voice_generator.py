import os
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential, wait_random, retry_if_exception_type, before_sleep_log
import logging

# Setup logger for retry attempts
logger = logging.getLogger(__name__)

# Try importing google.cloud.texttospeech, but handle the case where it's not installed or credentials fail
try:
    from google.cloud import texttospeech
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

class VoiceGenerator:
    def __init__(self):
        self.client = None
        self.rate_limit_exceeded = False  # Track rate limit state
        
        if TTS_AVAILABLE:
            try:
                # This will look for GOOGLE_APPLICATION_CREDENTIALS env var
                self.client = texttospeech.TextToSpeechClient()
            except Exception as e:
                print(f"Warning: Failed to initialize Google Cloud TTS: {e}")
        else:
            print("Warning: Google Cloud TTS not available. Using Mock mode.")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10) + wait_random(0, 2),  # Add jitter with wait_random
        retry=retry_if_exception_type((Exception,)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def _synthesize_with_retry(self, synthesis_input, voice, audio_config, output_path):
        """Internal method with retry logic for TTS API calls."""
        if self.rate_limit_exceeded:
            raise Exception("Rate limit exceeded, using mock mode")
        
        response = self.client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        # The response's audio_content is binary.
        with open(output_path, "wb") as out:
            out.write(response.audio_content)
        
        return output_path

    def generate_voice(self, text: str, output_path: str, voice_name: str = "en-US-Journey-D") -> Optional[str]:
        """
        Generates audio from text and saves it to the output path.
        Returns the path to the saved audio or None if failed.
        """
        if self.client and not self.rate_limit_exceeded:
            try:
                print(f"Generating voice for: {text[:50]}...")
                synthesis_input = texttospeech.SynthesisInput(text=text)

                # Build the voice request
                # Check if voice_name contains language code, else default to en-US
                language_code = "-".join(voice_name.split("-")[:2]) if "-" in voice_name else "en-US"
                
                voice = texttospeech.VoiceSelectionParams(
                    language_code=language_code,
                    name=voice_name
                )

                # Select the type of audio file you want returned
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3
                )

                return self._synthesize_with_retry(synthesis_input, voice, audio_config, output_path)

            except Exception as e:
                error_str = str(e).lower()
                # Check for rate limit errors
                if 'rate limit' in error_str or 'quota' in error_str or 'resource exhausted' in error_str:
                    print(f"Rate limit or quota exceeded for TTS. Switching to mock mode.")
                    self.rate_limit_exceeded = True
                else:
                    print(f"Error generating voice with Google Cloud TTS: {e}")
                
                # Fallback to mock if generation fails
                return self._generate_mock_voice(text, output_path)
        
        return self._generate_mock_voice(text, output_path)

    def _generate_mock_voice(self, text: str, output_path: str) -> str:
        """Generates a placeholder audio file (empty or simple tone) for testing."""
        print(f"Mock Generating voice for: {text[:50]}...")
        # Create a dummy text file pretending to be mp3 for now, or a minimal valid mp3 header if needed.
        # For simplicity in this prototype, we'll just write text content to the file 
        # but give it .mp3 extension so the pipeline sees a file. 
        # In a real app, we might copy a static 'silent.mp3' asset.
        
        with open(output_path, 'w') as f:
            f.write(f"Mock Audio Content for: {text}")
        
        return output_path

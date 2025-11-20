import os
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential, wait_random, retry_if_exception_type, before_sleep_log
import logging

# Setup logger for retry attempts
logger = logging.getLogger(__name__)

import yaml

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
        self.voice_profiles = {}
        self.load_voice_profiles()
        
        if TTS_AVAILABLE:
            try:
                # This will look for GOOGLE_APPLICATION_CREDENTIALS env var
                self.client = texttospeech.TextToSpeechClient()
            except Exception as e:
                print(f"Warning: Failed to initialize Google Cloud TTS: {e}")
        else:
            print("Warning: Google Cloud TTS not available. Using Mock mode.")

    def load_voice_profiles(self):
        """Loads voice profiles from config file."""
        try:
            # Construct path relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, 'config', 'voices.yaml')
            
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.voice_profiles = yaml.safe_load(f)
                print(f"Loaded {len(self.voice_profiles)} voice profiles.")
            else:
                print(f"Warning: Voice config not found at {config_path}")
                self.voice_profiles = {}
        except Exception as e:
            print(f"Error loading voice profiles: {e}")
            self.voice_profiles = {}

    def get_voice_for_character(self, character_name: str) -> dict:
        """Determines the best voice profile for a given character name."""
        if not self.voice_profiles:
            return {}

        name_lower = character_name.lower()
        
        # 1. Check for Narrator
        if "narrator" in name_lower:
            return self.voice_profiles.get('narrator', {})
        
        # 2. Check for exact match in config (if we add specific characters later)
        if name_lower in self.voice_profiles:
            return self.voice_profiles[name_lower]

        # 3. Gender/Age Heuristics
        female_keywords = ['mrs.', 'ms.', 'miss', 'lady', 'woman', 'mother', 'mom', 'aunt', 'sister', 'queen', 'princess']
        child_keywords = ['child', 'kid', 'boy', 'girl', 'young', 'baby', 'son', 'daughter']
        
        if any(k in name_lower for k in child_keywords):
            return self.voice_profiles.get('child_default', self.voice_profiles.get('female_default', {}))
            
        if any(k in name_lower for k in female_keywords):
            return self.voice_profiles.get('female_default', {})

        # 4. Default to male
        return self.voice_profiles.get('male_default', {})

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

    def generate_voice(self, text: str, output_path: str, voice_name: str = "en-US-Journey-D", voice_params: dict = None) -> Optional[str]:
        """
        Generates audio from text and saves it to the output path.
        Returns the path to the saved audio or None if failed.
        
        Args:
            text: The text to synthesize.
            output_path: Path to save the MP3 file.
            voice_name: Default voice name if voice_params is not provided.
            voice_params: Dictionary containing voice configuration (name, language_code, speaking_rate, pitch).
        """
        if self.client and not self.rate_limit_exceeded:
            try:
                print(f"Generating voice for: {text[:50]}...")
                synthesis_input = texttospeech.SynthesisInput(text=text)

                # Determine voice settings
                language_code = "en-US"
                speaking_rate = 1.0
                pitch = 0.0
                
                if voice_params:
                    voice_name = voice_params.get('name', voice_name)
                    language_code = voice_params.get('language_code', "en-US")
                    speaking_rate = voice_params.get('speaking_rate', 1.0)
                    pitch = voice_params.get('pitch', 0.0)
                elif "-" in voice_name:
                     language_code = "-".join(voice_name.split("-")[:2])

                voice = texttospeech.VoiceSelectionParams(
                    language_code=language_code,
                    name=voice_name
                )

                # Select the type of audio file you want returned
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=speaking_rate,
                    pitch=pitch
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

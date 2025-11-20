import os
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential, wait_random, retry_if_exception_type, before_sleep_log
import logging
import yaml
import tempfile
import shutil
from moviepy import concatenate_audioclips, AudioFileClip

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
        
        try:
            from moviepy import AudioClip
            import numpy as np
            
            # Generate 3 seconds of silence (or a sine wave if we wanted sound)
            duration = 3.0
            
            def make_frame(t):
                return np.sin(2 * np.pi * 440 * t) * 0.1 # Sine wave at 440Hz, low volume
                
            # Create a mono audio clip
            # Note: make_frame for audio returns a numpy array of shape (n_samples, n_channels) or just (n_samples)
            # MoviePy v2 might expect (n_samples, n_channels)
            
            # Let's just make silence to be safe and simple
            # clip = AudioClip(lambda t: [0], duration=duration) # Mono silence
            
            # Actually, let's use a sine wave so we can hear it if needed
            # 44100 Hz
            
            # Simple way: create a silent clip
            # from moviepy.audio.AudioClip import AudioClip
            
            # Let's try to create a valid MP3 using moviepy
            # Since we already imported moviepy at top level
            
            # We need to handle the case where moviepy might not be fully set up or numpy missing
            # But we are in a dev environment where we installed requirements.
            
            # Create a 2-second silent clip
            # In MoviePy v2, AudioClip takes a make_frame function
            
            def sine_tone(t):
                return [np.sin(2 * np.pi * 440 * t) * 0.1] # Mono
                
            clip = AudioClip(sine_tone, duration=2.0)
            clip.write_audiofile(output_path, fps=44100, logger=None)
            
        except Exception as e:
            print(f"Error generating mock audio with MoviePy: {e}")
            # Fallback to text file if moviepy fails (but this will break downstream)
            with open(output_path, 'w') as f:
                f.write(f"Mock Audio Content for: {text}")
        
        return output_path

    def generate_conversation(self, audio_script: list, output_path: str) -> Optional[str]:
        """
        Generates a conversation audio file from a script.
        
        Args:
            audio_script: List of dicts with 'speaker' and 'text'.
            output_path: Path to save the final MP3.
        """
        # Check if we are effectively in mock mode
        if not self.client or self.rate_limit_exceeded:
             print("Mock generating conversation...")
             with open(output_path, 'w') as f:
                 for segment in audio_script:
                     speaker = segment.get('speaker', 'Unknown')
                     text = segment.get('text', '')
                     f.write(f"{speaker}: {text}\n")
             return output_path

        # Real generation
        temp_files = []
        clips = []
        temp_dir = None
        
        try:
            # Create a temp directory for segments
            temp_dir = tempfile.mkdtemp()
            
            for i, segment in enumerate(audio_script):
                speaker = segment.get('speaker', 'Narrator')
                text = segment.get('text', '')
                
                if not text.strip():
                    continue
                    
                # Get voice profile
                voice_params = self.get_voice_for_character(speaker)
                
                # Generate segment audio
                segment_path = os.path.join(temp_dir, f"seg_{i}.mp3")
                result = self.generate_voice(text, segment_path, voice_params=voice_params)
                
                if result:
                    temp_files.append(result)
                    try:
                        clip = AudioFileClip(result)
                        clips.append(clip)
                    except Exception as e:
                        print(f"Error loading audio clip {result}: {e}")

            if not clips:
                print("No audio clips generated for conversation.")
                return None

            # Concatenate
            final_clip = concatenate_audioclips(clips)
            final_clip.write_audiofile(output_path, logger=None)
            
            # Close clips to release file handles
            for clip in clips:
                clip.close()
            final_clip.close()
            
            return output_path

        except Exception as e:
            print(f"Error generating conversation: {e}")
            # Fallback to mock on error
            return self._generate_mock_voice("Conversation generation failed", output_path)
        finally:
            # Cleanup temp dir
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

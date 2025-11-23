from google import genai
from google.genai import types
import os
import json
import re
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
import logging

# Setup logger for retry attempts
logger = logging.getLogger(__name__)

class ScreenplayGenerator:
    def __init__(self):
        # Try to get API key from environment (GOOGLE_API_KEY or GEMINI_API_KEY)
        self.api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        
        # Check if using Vertex AI
        use_vertexai = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true"
        
        if use_vertexai:
            # Vertex AI mode
            project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
            location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
            if not project_id:
                raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set for Vertex AI.")
            self.client = genai.Client(vertexai=True, project=project_id, location=location)
            self.model_name = 'gemini-1.5-pro'
            self.api_mode = 'vertex'
        elif self.api_key:
            # Developer API mode
            self.client = genai.Client(api_key=self.api_key)
            self.model_name = 'gemini-2.0-flash-exp'  # Try latest experimental model first
            self.api_mode = 'developer'
        else:
            raise ValueError("Either GOOGLE_API_KEY/GEMINI_API_KEY or GOOGLE_GENAI_USE_VERTEXAI with GOOGLE_CLOUD_PROJECT must be set.")
        
        # Try to verify the model works, if not, find an alternative
        self._verify_or_find_model()
    
    def _verify_or_find_model(self):
        """Verify the default model works, or find an available alternative."""
        try:
            # Try a simple test generation with the default model
            test_response = self.client.models.generate_content(
                model=self.model_name,
                contents="Test"
            )
            print(f"✓ Using model: {self.model_name}")
        except Exception as e:
            error_str = str(e).lower()
            if '404' in error_str or 'not found' in error_str:
                print(f"⚠ Model '{self.model_name}' not available. Searching for alternatives...")
                self._find_best_available_model()
            else:
                print(f"Warning: Model verification failed: {e}")
                # Try to continue anyway
    
    def _find_best_available_model(self):
        """Fetch available models and select the best Gemini model."""
        try:
            # List available models
            models = self.client.models.list()
            
            # Filter for Gemini models that support generateContent
            gemini_models = []
            for model in models:
                model_name = model.name
                # Extract just the model ID (e.g., "gemini-1.5-flash" from "models/gemini-1.5-flash")
                if '/' in model_name:
                    model_id = model_name.split('/')[-1]
                else:
                    model_id = model_name
                
                # Check if it's a Gemini model and supports content generation
                if 'gemini' in model_id.lower():
                    # Check if it supports generateContent
                    if hasattr(model, 'supported_generation_methods'):
                        if 'generateContent' in model.supported_generation_methods:
                            gemini_models.append(model_id)
                    else:
                        # If we can't check, assume it works
                        gemini_models.append(model_id)
            
            if gemini_models:
                # Prefer models in this order: 2.0 > 1.5-pro > 1.5-flash > others
                preferred_order = ['2.0', '1.5-pro', '1.5-flash', 'pro', 'flash']
                
                best_model = None
                for preference in preferred_order:
                    for model in gemini_models:
                        if preference in model.lower():
                            best_model = model
                            break
                    if best_model:
                        break
                
                # If no preferred model found, use the first available
                if not best_model:
                    best_model = gemini_models[0]
                
                self.model_name = best_model
                print(f"✓ Found alternative model: {self.model_name}")
                print(f"  Available Gemini models: {', '.join(gemini_models[:5])}")
            else:
                print("✗ No Gemini models found. Using default model anyway.")
                
        except Exception as e:
            print(f"Warning: Could not fetch available models: {e}")
            print(f"Continuing with default model: {self.model_name}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def paragraph_to_screenplay(self, paragraph):
        """Converts a paragraph into a screenplay object using Gemini API.
        
        Returns:
            dict: Parsed screenplay with scene_description, dialogues, voiceover_text, and character traits
                  Falls back to raw text structure if JSON parsing fails
        """
        prompt = f"""Convert the following paragraph into a detailed cinematic screenplay object WITH CHARACTER ANALYSIS:
        {paragraph}

        You MUST respond with ONLY a valid JSON object (no markdown, no extra text).
        
        CRITICAL: For each speaker in the audio_script, analyze the text and infer character traits to help select an appropriate voice.
        
        The JSON structure must be:
        {{
          "scene_description": "Detailed cinematic scene description for image generation",
          "audio_script": [
            {{
              "speaker": "Narrator",
              "text": "Narration text...",
              "traits": {{
                "age": "adult",
                "gender": "neutral",
                "personality": ["calm", "authoritative"],
                "emotional_tone": "neutral"
              }}
            }},
            {{
              "speaker": "Character Name",
              "text": "Dialogue line...",
              "traits": {{
                "age": "child|teen|young_adult|adult|elderly",
                "gender": "male|female|neutral",
                "personality": ["shy", "bold", "gentle", "energetic", "wise", "dramatic"],
                "emotional_tone": "soft|energetic|calm|dramatic|cheerful|sad"
              }}
            }}
          ],
          "dialogues": [], 
          "voiceover_text": "Full narration text (legacy support)"
        }}
        
        TRAIT DETECTION GUIDELINES:
        - age: Infer from descriptors (little, young, old, elderly, child, teen, etc.) or context
        - gender: Infer from pronouns (he/she), titles (Mr/Mrs), or character names
        - personality: Extract from adjectives describing the character or their actions
        - emotional_tone: Infer from how they speak (whispered=soft, shouted=energetic, etc.)
        
        If traits cannot be inferred, use reasonable defaults:
        - Narrator: age="adult", gender="neutral", personality=["calm"], emotional_tone="neutral"
        - Unknown character: age="adult", gender="neutral", personality=[], emotional_tone="neutral"
        
        The 'audio_script' should be an ordered list of all spoken parts, including narration and character dialogue, in the correct sequence.
        If there are no dialogues, 'audio_script' should contain just the Narrator part.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            response_text = response.text.strip()
            
            # Try to parse as JSON
            screenplay = self._parse_json_response(response_text)
            
            # Validate required fields
            if self._validate_screenplay(screenplay):
                return screenplay
            else:
                # Fallback if validation fails
                return self._create_fallback_screenplay(paragraph, response_text)
                
        except Exception as e:
            print(f"Error generating screenplay: {e}")
            # Return fallback structure
            return self._create_fallback_screenplay(paragraph, str(e))

    def _parse_json_response(self, response_text):
        """Attempts to extract and parse JSON from response.
        
        Handles cases where Gemini wraps JSON in markdown code blocks.
        """
        # Remove markdown code blocks if present
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        
        # Parse JSON
        return json.loads(response_text)
    
    def _validate_screenplay(self, screenplay):
        """Validates that screenplay has required fields."""
        if not isinstance(screenplay, dict):
            return False
        
        # Check for audio_script (new format)
        if 'audio_script' in screenplay:
            if not isinstance(screenplay['audio_script'], list):
                return False
            for segment in screenplay['audio_script']:
                if not isinstance(segment, dict):
                    return False
                if 'speaker' not in segment or 'text' not in segment:
                    return False
            return True
            
        # Legacy check
        required_fields = ['scene_description', 'dialogues', 'voiceover_text']
        for field in required_fields:
            if field not in screenplay:
                return False
        
        return True
    
    def _create_fallback_screenplay(self, paragraph, error_info=""):
        """Creates a fallback screenplay structure when JSON parsing fails."""
        return {
            "scene_description": f"A scene depicting: {paragraph[:150]}...",
            "audio_script": [
                {"speaker": "Narrator", "text": paragraph[:500]}
            ],
            "dialogues": [],
            "voiceover_text": paragraph[:500],
            "_fallback": True,
            "_error": error_info
        }

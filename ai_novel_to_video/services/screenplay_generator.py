import google.generativeai as genai
import os
import json
import re
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
import logging

# Setup logger for retry attempts
logger = logging.getLogger(__name__)

class ScreenplayGenerator:
    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')

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
            dict: Parsed screenplay with scene_description, dialogues, voiceover_text
                  Falls back to raw text structure if JSON parsing fails
        """
        prompt = f"""Convert the following paragraph into a detailed cinematic screenplay object:
        {paragraph}

        You MUST respond with ONLY a valid JSON object (no markdown, no extra text).
        
        The JSON structure must be:
        {{
          "scene_description": "Detailed cinematic scene description for image generation",
          "audio_script": [
            {{
              "speaker": "Narrator",
              "text": "Narration text..."
            }},
            {{
              "speaker": "Character Name",
              "text": "Dialogue line..."
            }}
          ],
          "dialogues": [], 
          "voiceover_text": "Full narration text (legacy support)"
        }}
        
        The 'audio_script' should be an ordered list of all spoken parts, including narration and character dialogue, in the correct sequence.
        If there are no dialogues, 'audio_script' should contain just the Narrator part.
        """

        try:
            response = self.model.generate_content(prompt)
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

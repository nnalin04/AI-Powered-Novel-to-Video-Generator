import google.generativeai as genai
import os

class ScreenplayGenerator:
    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')

    def paragraph_to_screenplay(self, paragraph):
        """Converts a paragraph into a screenplay object using Gemini API."""
        prompt = f"""Convert the following paragraph into a detailed cinematic screenplay object:
        {paragraph}

        The screenplay object should include:
        - scene_description: A detailed cinematic scene description
        - dialogues: A list of dialogues, with each dialogue including the character and the line
        - voiceover_text: Narration text for TTS

        The output should be a JSON object with the following structure:
        {{
          "scene_description": "Detailed cinematic scene description",
          "dialogues": [
            {{
              "character": "A",
              "line": "..."
            }},
            {{
              "character": "B",
              "line": "..."
            }}
          ],
          "voiceover_text": "Narration text for TTS"
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating screenplay: {e}"

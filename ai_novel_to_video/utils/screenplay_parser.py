"""
ScreenplayParser - Utility for extracting and processing screenplay data.

This module provides helper functions to extract specific information from
parsed screenplay dictionaries returned by the ScreenplayGenerator.
"""

class ScreenplayParser:
    """Utility class for parsing screenplay dictionaries."""
    
    @staticmethod
    def extract_scene_description(screenplay):
        """Extract the scene description for image generation.
        
        Args:
            screenplay (dict): Parsed screenplay dictionary
            
        Returns:
            str: Scene description suitable for image generation prompts
        """
        if not isinstance(screenplay, dict):
            return ""
        
        return screenplay.get('scene_description', '')
    
    @staticmethod
    def extract_voiceover_text(screenplay):
        """Extract the voiceover/narration text for TTS.
        
        Args:
            screenplay (dict): Parsed screenplay dictionary
            
        Returns:
            str: Narration text for text-to-speech
        """
        if not isinstance(screenplay, dict):
            return ""
        
        return screenplay.get('voiceover_text', '')
    
    @staticmethod
    def extract_dialogues(screenplay):
        """Extract character dialogues.
        
        Args:
            screenplay (dict): Parsed screenplay dictionary
            
        Returns:
            list: List of dialogue dicts with 'character' and 'line' keys
        """
        if not isinstance(screenplay, dict):
            return []
        
        dialogues = screenplay.get('dialogues', [])
        
        # Validate structure
        if not isinstance(dialogues, list):
            return []
        
        # Filter out malformed dialogues
        valid_dialogues = []
        for dialogue in dialogues:
            if isinstance(dialogue, dict) and 'character' in dialogue and 'line' in dialogue:
                valid_dialogues.append(dialogue)
        
        return valid_dialogues
    
    @staticmethod
    def has_dialogues(screenplay):
        """Check if screenplay contains any dialogues.
        
        Args:
            screenplay (dict): Parsed screenplay dictionary
            
        Returns:
            bool: True if screenplay has dialogues, False otherwise
        """
        dialogues = ScreenplayParser.extract_dialogues(screenplay)
        return len(dialogues) > 0
    
    @staticmethod
    def is_fallback(screenplay):
        """Check if screenplay used fallback mode.
        
        Args:
            screenplay (dict): Parsed screenplay dictionary
            
        Returns:
            bool: True if screenplay is a fallback, False if properly parsed
        """
        if not isinstance(screenplay, dict):
            return True
        
        return screenplay.get('_fallback', False)
    
    @staticmethod
    def get_image_prompt(screenplay, fallback_text=""):
        """Get a suitable prompt for image generation.
        
        Args:
            screenplay (dict): Parsed screenplay dictionary
            fallback_text (str): Fallback text to use if scene_description is empty
            
        Returns:
            str: Prompt suitable for image generation
        """
        scene_desc = ScreenplayParser.extract_scene_description(screenplay)
        
        if scene_desc:
            return f"Cinematic shot: {scene_desc}"
        elif fallback_text:
            return f"Cinematic shot of: {fallback_text[:100]}"
        else:
            return "Cinematic scene"
    
    @staticmethod
    def get_narration_text(screenplay, fallback_text=""):
        """Get narration text for voice generation.
        
        Args:
            screenplay (dict): Parsed screenplay dictionary
            fallback_text (str): Fallback text to use if voiceover_text is empty
            
        Returns:
            str: Text for narration voice generation
        """
        voiceover = ScreenplayParser.extract_voiceover_text(screenplay)
        
        if voiceover:
            return voiceover
        elif fallback_text:
            return fallback_text[:500]
        else:
            return ""

import pytest
import json
from unittest.mock import MagicMock, patch
from ai_novel_to_video.services.screenplay_generator import ScreenplayGenerator
from ai_novel_to_video.utils.screenplay_parser import ScreenplayParser


class TestScreenplayGenerator:
    """Tests for ScreenplayGenerator with JSON parsing."""
    
    def test_parse_valid_json(self):
        """Test parsing of valid JSON response."""
        generator = ScreenplayGenerator.__new__(ScreenplayGenerator)
        
        valid_json = '''
        {
            "scene_description": "A beautiful sunset over mountains",
            "dialogues": [
                {"character": "John", "line": "What a view!"}
            ],
            "voiceover_text": "The sun sets behind the mountains."
        }
        '''
        
        result = generator._parse_json_response(valid_json)
        
        assert isinstance(result, dict)
        assert result['scene_description'] == "A beautiful sunset over mountains"
        assert len(result['dialogues']) == 1
        assert result['voiceover_text'] == "The sun sets behind the mountains."
    
    def test_parse_json_with_markdown(self):
        """Test parsing JSON wrapped in markdown code blocks."""
        generator = ScreenplayGenerator.__new__(ScreenplayGenerator)
        
        markdown_wrapped = '''```json
        {
            "scene_description": "A dark forest",
            "dialogues": [],
            "voiceover_text": "The forest is silent."
        }
        ```'''
        
        result = generator._parse_json_response(markdown_wrapped)
        
        assert isinstance(result, dict)
        assert result['scene_description'] == "A dark forest"
        assert result['dialogues'] == []
    
    def test_validate_complete_screenplay(self):
        """Test validation of a complete screenplay."""
        generator = ScreenplayGenerator.__new__(ScreenplayGenerator)
        
        screenplay = {
            "scene_description": "Test scene",
            "dialogues": [
                {"character": "A", "line": "Hello"}
            ],
            "voiceover_text": "Test narration"
        }
        
        assert generator._validate_screenplay(screenplay) == True
    
    def test_validate_missing_field(self):
        """Test validation fails with missing field."""
        generator = ScreenplayGenerator.__new__(ScreenplayGenerator)
        
        screenplay = {
            "scene_description": "Test scene",
            "dialogues": []
            # Missing voiceover_text
        }
        
        assert generator._validate_screenplay(screenplay) == False
    
    def test_validate_malformed_dialogues(self):
        """Test validation fails with malformed dialogues."""
        generator = ScreenplayGenerator.__new__(ScreenplayGenerator)
        
        screenplay = {
            "scene_description": "Test scene",
            "dialogues": [
                {"character": "A"}  # Missing 'line'
            ],
            "voiceover_text": "Test"
        }
        
        assert generator._validate_screenplay(screenplay) == False
    
    def test_create_fallback_screenplay(self):
        """Test fallback screenplay creation."""
        generator = ScreenplayGenerator.__new__(ScreenplayGenerator)
        
        paragraph = "This is a test paragraph for the fallback."
        fallback = generator._create_fallback_screenplay(paragraph, "Test error")
        
        assert isinstance(fallback, dict)
        assert 'scene_description' in fallback
        assert 'dialogues' in fallback
        assert 'voiceover_text' in fallback
        assert fallback['_fallback'] == True
        assert fallback['_error'] == "Test error"
        assert len(fallback['dialogues']) == 0


class TestScreenplayParser:
    """Tests for ScreenplayParser utility."""
    
    def test_extract_scene_description(self):
        """Test extracting scene description."""
        screenplay = {
            "scene_description": "A bustling city street",
            "dialogues": [],
            "voiceover_text": "The city never sleeps."
        }
        
        result = ScreenplayParser.extract_scene_description(screenplay)
        assert result == "A bustling city street"
    
    def test_extract_voiceover_text(self):
        """Test extracting voiceover text."""
        screenplay = {
            "scene_description": "Test",
            "dialogues": [],
            "voiceover_text": "This is the narration."
        }
        
        result = ScreenplayParser.extract_voiceover_text(screenplay)
        assert result == "This is the narration."
    
    def test_extract_dialogues(self):
        """Test extracting dialogues."""
        screenplay = {
            "scene_description": "Test",
            "dialogues": [
                {"character": "Alice", "line": "Hello"},
                {"character": "Bob", "line": "Hi there"}
            ],
            "voiceover_text": "Test"
        }
        
        result = ScreenplayParser.extract_dialogues(screenplay)
        assert len(result) == 2
        assert result[0]['character'] == "Alice"
        assert result[1]['line'] == "Hi there"
    
    def test_extract_dialogues_filters_malformed(self):
        """Test that malformed dialogues are filtered out."""
        screenplay = {
            "scene_description": "Test",
            "dialogues": [
                {"character": "Alice", "line": "Hello"},
                {"character": "Bob"},  # Missing 'line'
                {"line": "Test"}  # Missing 'character'
            ],
            "voiceover_text": "Test"
        }
        
        result = ScreenplayParser.extract_dialogues(screenplay)
        assert len(result) == 1
        assert result[0]['character'] == "Alice"
    
    def test_has_dialogues(self):
        """Test checking if screenplay has dialogues."""
        screenplay_with = {
            "scene_description": "Test",
            "dialogues": [{"character": "A", "line": "B"}],
            "voiceover_text": "Test"
        }
        
        screenplay_without = {
            "scene_description": "Test",
            "dialogues": [],
            "voiceover_text": "Test"
        }
        
        assert ScreenplayParser.has_dialogues(screenplay_with) == True
        assert ScreenplayParser.has_dialogues(screenplay_without) == False
    
    def test_is_fallback(self):
        """Test detecting fallback screenplays."""
        fallback_screenplay = {
            "scene_description": "Test",
            "dialogues": [],
            "voiceover_text": "Test",
            "_fallback": True
        }
        
        normal_screenplay = {
            "scene_description": "Test",
            "dialogues": [],
            "voiceover_text": "Test"
        }
        
        assert ScreenplayParser.is_fallback(fallback_screenplay) == True
        assert ScreenplayParser.is_fallback(normal_screenplay) == False
    
    def test_get_image_prompt(self):
        """Test getting image prompt from screenplay."""
        screenplay = {
            "scene_description": "A mystical forest at dawn",
            "dialogues": [],
            "voiceover_text": "Test"
        }
        
        result = ScreenplayParser.get_image_prompt(screenplay)
        assert "Cinematic shot:" in result
        assert "mystical forest" in result
    
    def test_get_image_prompt_with_fallback(self):
        """Test image prompt with fallback text."""
        screenplay = {
            "scene_description": "",
            "dialogues": [],
            "voiceover_text": "Test"
        }
        
        result = ScreenplayParser.get_image_prompt(screenplay, "A dark alley")
        assert "dark alley" in result
    
    def test_get_narration_text(self):
        """Test getting narration text."""
        screenplay = {
            "scene_description": "Test",
            "dialogues": [],
            "voiceover_text": "The narrator speaks..."
        }
        
        result = ScreenplayParser.get_narration_text(screenplay)
        assert result == "The narrator speaks..."
    
    def test_get_narration_text_with_fallback(self):
        """Test narration text with fallback."""
        screenplay = {
            "scene_description": "Test",
            "dialogues": [],
            "voiceover_text": ""
        }
        
        fallback = "This is a fallback narration text."
        result = ScreenplayParser.get_narration_text(screenplay, fallback)
        assert result == fallback

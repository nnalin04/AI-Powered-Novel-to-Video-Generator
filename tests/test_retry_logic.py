import pytest
import os
from unittest.mock import MagicMock, patch
from ai_novel_to_video.services.image_generator import ImageGenerator
from ai_novel_to_video.services.voice_generator import VoiceGenerator


class TestRetryLogic:
    """Tests for retry logic and fallback behavior."""
    
    def test_image_generator_quota_detection(self):
        """Test that ImageGenerator detects quota errors and switches to mock."""
        generator = ImageGenerator.__new__(ImageGenerator)
        generator.project_id = "test-project"
        generator.location = "us-central1"
        generator.model = MagicMock()
        generator.quota_exceeded = False
        
        # Simulate quota exceeded error
        generator.model.generate_images.side_effect = Exception("Quota exceeded: Resource exhausted")        
        result = generator.generate_image("Test prompt", "/tmp/test.png")
        
        # Should have detected quota and set flag
        assert generator.quota_exceeded == True
        # Should still return a path (mock)
        assert result == "/tmp/test.png"
    
    def test_image_generator_stops_retrying_after_quota(self):
        """Test that ImageGenerator stops trying real API after quota exceeded."""
        generator = ImageGenerator.__new__(ImageGenerator)
        generator.project_id = "test-project"
        generator.model = MagicMock()
        generator.quota_exceeded = True  # Already exceeded
        
        with patch.object(generator, '_generate_mock_image', return_value="/tmp/mock.png") as mock_gen:
            result = generator.generate_image("Test prompt", "/tmp/test.png")
            
            # Should not have tried real API
            generator.model.generate_images.assert_not_called()
            # Should have used mock
            mock_gen.assert_called_once()
    
    def test_voice_generator_rate_limit_detection(self):
        """Test that VoiceGenerator detects rate limit errors."""
        generator = VoiceGenerator.__new__(VoiceGenerator)
        generator.client = MagicMock()
        generator.rate_limit_exceeded = False
        
        # Create a mock that will be called by _synthesize_with_retry
        def raise_rate_limit(*args, **kwargs):
            raise Exception("Rate limit exceeded for TTS")
        
        # Mock the retry wrapper to fail immediately
        with patch.object(generator, '_synthesize_with_retry', side_effect=raise_rate_limit):
            result = generator.generate_voice("Test text", "/tmp/test.mp3")
        
        # Should have detected rate limit  
        assert generator.rate_limit_exceeded == True
        # Should still return a path (mock)
        assert result == "/tmp/test.mp3"
    
    def test_image_generator_fallback(self):
        """Test that ImageGenerator falls back to mock on persistent failures."""
        img_gen = ImageGenerator.__new__(ImageGenerator)
        img_gen.project_id = "test"
        img_gen.model = MagicMock()
        img_gen.quota_exceeded = False
        img_gen.model.generate_images.side_effect = Exception("Persistent failure")
        
        result = img_gen.generate_image("Test", "/tmp/test.png")
        # Should have used mock (path still returned)
        assert result == "/tmp/test.png"
        # Should have detected and set quota flag (fallback behavior)
        assert img_gen.quota_exceeded == False  # Not a quota error, just generic failure


class TestRetryConfiguration:
    """Tests verifying retry configuration is properly applied."""
    
    def test_retry_decorators_are_applied(self):
        """Verify that retry decorators are applied to service methods."""
        from ai_novel_to_video.services.screenplay_generator import ScreenplayGenerator
        from ai_novel_to_video.services.image_generator import ImageGenerator
        from ai_novel_to_video.services.voice_generator import VoiceGenerator
        
        # Check that retry decorator is applied (methods have __wrapped__ or retry attributes)
        # This verifies the decorator syntax is correct
        assert hasattr(ScreenplayGenerator.paragraph_to_screenplay, '__wrapped__') or \
               hasattr(ScreenplayGenerator.paragraph_to_screenplay, 'retry')
        
        assert hasattr(ImageGenerator._generate_with_retry, '__wrapped__') or \
               hasattr(ImageGenerator._generate_with_retry, 'retry')
               
        assert hasattr(VoiceGenerator._synthesize_with_retry, '__wrapped__') or \
               hasattr(VoiceGenerator._synthesize_with_retry, 'retry')

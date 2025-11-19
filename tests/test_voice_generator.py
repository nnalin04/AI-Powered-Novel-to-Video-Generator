import pytest
import os
from unittest.mock import MagicMock, patch
from ai_novel_to_video.services.voice_generator import VoiceGenerator

@pytest.fixture
def mock_texttospeech():
    with patch('ai_novel_to_video.services.voice_generator.texttospeech') as mock:
        yield mock

def test_init_mock_mode_no_client(mock_texttospeech):
    """Test initialization falls back to mock mode if import fails or client init fails."""
    # Simulate client init failure
    mock_texttospeech.TextToSpeechClient.side_effect = Exception("Auth Error")
    
    generator = VoiceGenerator()
    assert generator.client is None

def test_init_success(mock_texttospeech):
    """Test initialization success."""
    generator = VoiceGenerator()
    mock_texttospeech.TextToSpeechClient.assert_called_once()
    assert generator.client is not None

def test_generate_voice_mock(tmp_path):
    """Test mock generation creates a file."""
    # Force mock mode by patching TTS_AVAILABLE to False or ensuring client is None
    with patch('ai_novel_to_video.services.voice_generator.TTS_AVAILABLE', False):
        generator = VoiceGenerator()
        output_file = tmp_path / "test_voice.mp3"
        
        result = generator.generate_voice("Hello world", str(output_file))
        
        assert result == str(output_file)
        assert os.path.exists(output_file)
        with open(output_file, 'r') as f:
            content = f.read()
            assert "Mock Audio Content" in content

def test_generate_voice_google_success(mock_texttospeech, tmp_path):
    """Test Google TTS generation success path."""
    generator = VoiceGenerator()
    
    # Mock the response
    mock_response = MagicMock()
    mock_response.audio_content = b"fake_audio_data"
    generator.client.synthesize_speech.return_value = mock_response
    
    output_file = tmp_path / "google_voice.mp3"
    result = generator.generate_voice("Hello world", str(output_file))
    
    # Verify call arguments
    generator.client.synthesize_speech.assert_called_once()
    
    # Verify SynthesisInput was created with correct text
    mock_texttospeech.SynthesisInput.assert_called_with(text="Hello world")
    
    # Verify VoiceSelectionParams was created with correct name
    mock_texttospeech.VoiceSelectionParams.assert_called_with(language_code="en-US", name="en-US-Journey-D")
    
    assert result == str(output_file)
    assert os.path.exists(output_file)
    with open(output_file, 'rb') as f:
        assert f.read() == b"fake_audio_data"

def test_generate_voice_google_failure_fallback(mock_texttospeech, tmp_path):
    """Test fallback to mock if Google TTS fails."""
    generator = VoiceGenerator()
    
    # Mock failure
    generator.client.synthesize_speech.side_effect = Exception("API Error")
    
    output_file = tmp_path / "fallback_voice.mp3"
    result = generator.generate_voice("Hello world", str(output_file))
    
    assert result == str(output_file)
    assert os.path.exists(output_file)
    # Should contain mock text content, not binary
    with open(output_file, 'r') as f:
        assert "Mock Audio Content" in f.read()

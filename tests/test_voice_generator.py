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

def test_get_voice_for_character():
    """Test voice selection logic."""
    # We need to mock the config loading or ensure it loads correctly.
    # Since the class loads from a file, we might want to patch load_voice_profiles 
    # or just rely on the default empty dict if file missing, but better to patch.
    
    with patch('ai_novel_to_video.services.voice_generator.VoiceGenerator.load_voice_profiles') as mock_load:
        generator = VoiceGenerator()
        # Manually set profiles for testing
        generator.voice_profiles = {
            'narrator': {'name': 'NarratorVoice'},
            'female_default': {'name': 'FemaleVoice'},
            'male_default': {'name': 'MaleVoice'},
            'child_default': {'name': 'ChildVoice'},
            'queen': {'name': 'QueenVoice'}
        }
        
        # Test Narrator
        assert generator.get_voice_for_character("Narrator")['name'] == 'NarratorVoice'
        
        # Test Exact Match
        assert generator.get_voice_for_character("Queen")['name'] == 'QueenVoice'
        
        # Test Female Heuristics
        assert generator.get_voice_for_character("Mrs. Smith")['name'] == 'FemaleVoice'
        assert generator.get_voice_for_character("Lady Jane")['name'] == 'FemaleVoice'
        
        # Test Child Heuristics
        assert generator.get_voice_for_character("Little Boy")['name'] == 'ChildVoice'
        
        # Test Default (Male)
        assert generator.get_voice_for_character("John Doe")['name'] == 'MaleVoice'

@patch('ai_novel_to_video.services.voice_generator.concatenate_audioclips')
@patch('ai_novel_to_video.services.voice_generator.AudioFileClip')
def test_generate_conversation(mock_audio_clip, mock_concat, tmp_path):
    """Test conversation generation orchestration."""
    # Force mock mode for simplicity of testing logic flow
    with patch('ai_novel_to_video.services.voice_generator.TTS_AVAILABLE', False):
        generator = VoiceGenerator()
        # Override client to ensure we hit the "Real generation" block if we want to test that,
        # BUT the code checks `if not self.client or self.rate_limit_exceeded`.
        # To test the "Real generation" block (lines 190+), we need self.client to be Truthy.
        generator.client = MagicMock() 
        generator.rate_limit_exceeded = False
        
        # Mock generate_voice to return a path
        generator.generate_voice = MagicMock(side_effect=lambda text, path, **kwargs: path)
        
        script = [
            {'speaker': 'Narrator', 'text': 'Intro'},
            {'speaker': 'Alice', 'text': 'Hello'},
        ]
        output_file = tmp_path / "conversation.mp3"
        
        result = generator.generate_conversation(script, str(output_file))
        
        # Verify generate_voice called twice
        assert generator.generate_voice.call_count == 2
        
        # Verify moviepy calls
        assert mock_audio_clip.call_count == 2
        mock_concat.assert_called_once()
        mock_concat.return_value.write_audiofile.assert_called_once()


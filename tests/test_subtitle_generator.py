import pytest
import os
from unittest.mock import MagicMock, patch
from ai_novel_to_video.services.subtitle_generator import SubtitleGenerator

@pytest.fixture
def mock_moviepy_audio():
    # Patch the service module's AudioFileClip directly
    with patch('ai_novel_to_video.services.subtitle_generator.MOVIEPY_AVAILABLE', True):
        mock_audio_cls = MagicMock()
        
        # Inject into module
        import ai_novel_to_video.services.subtitle_generator as sg
        orig_cls = getattr(sg, 'AudioFileClip', None)
        sg.AudioFileClip = mock_audio_cls
        
        yield mock_audio_cls
        
        if orig_cls:
            sg.AudioFileClip = orig_cls

def test_format_time():
    """Test timestamp formatting logic."""
    generator = SubtitleGenerator()
    
    assert generator._format_time(0) == "00:00:00,000"
    assert generator._format_time(1.5) == "00:00:01,500"
    assert generator._format_time(61.001) == "00:01:01,001"
    assert generator._format_time(3661.100) == "01:01:01,100"

def test_generate_srt_success(mock_moviepy_audio, tmp_path):
    """Test successful SRT generation with mocked audio duration."""
    generator = SubtitleGenerator()
    
    # Setup mock audio
    mock_instance = MagicMock()
    mock_instance.duration = 2.5
    mock_moviepy_audio.return_value.__enter__.return_value = mock_instance
    
    output_file = tmp_path / "test.srt"
    
    # Create dummy audio file
    audio_path = tmp_path / "audio.mp3"
    audio_path.touch()
    
    scenes = [
        {'text': "Scene 1", 'audio': str(audio_path)},
        {'text': "Scene 2", 'audio': str(audio_path)}
    ]
    
    result = generator.generate_srt(scenes, str(output_file))
    
    assert result == str(output_file)
    assert os.path.exists(output_file)
    
    with open(output_file, 'r') as f:
        content = f.read()
        
    # Check content structure
    expected_content = (
        "1\n"
        "00:00:00,000 --> 00:00:02,500\n"
        "Scene 1\n\n"
        "2\n"
        "00:00:02,500 --> 00:00:05,000\n"
        "Scene 2\n\n"
    )
    assert content == expected_content

def test_generate_srt_no_moviepy(tmp_path):
    """Test fallback duration when moviepy is missing."""
    with patch('ai_novel_to_video.services.subtitle_generator.MOVIEPY_AVAILABLE', False):
        generator = SubtitleGenerator()
        output_file = tmp_path / "fallback.srt"
        
        scenes = [{'text': "Fallback Scene", 'audio': "dummy.mp3"}]
        
        result = generator.generate_srt(scenes, str(output_file))
        
        assert result == str(output_file)
        with open(output_file, 'r') as f:
            content = f.read()
            
        # Should use default duration of 5.0s
        assert "00:00:00,000 --> 00:00:05,000" in content

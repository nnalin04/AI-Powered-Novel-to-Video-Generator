import pytest
import os
from unittest.mock import MagicMock, patch
from ai_novel_to_video.services.video_assembler import VideoAssembler

@pytest.fixture
def mock_moviepy():
    # We will patch the attributes on the service module directly.
    # This avoids issues with where moviepy exports things.
    
    mock_img = MagicMock()
    mock_audio = MagicMock()
    mock_concat = MagicMock()
    
    # Force MOVIEPY_AVAILABLE to True
    with patch('ai_novel_to_video.services.video_assembler.MOVIEPY_AVAILABLE', True):
         # Inject mocks into the module
         # We need to import it first
         import ai_novel_to_video.services.video_assembler as va
         
         # Save originals if they exist
         orig_img = getattr(va, 'ImageClip', None)
         orig_audio = getattr(va, 'AudioFileClip', None)
         orig_concat = getattr(va, 'concatenate_videoclips', None)
         
         va.ImageClip = mock_img
         va.AudioFileClip = mock_audio
         va.concatenate_videoclips = mock_concat
         
         yield mock_img, mock_audio, mock_concat
         
         # Cleanup (optional but good practice)
         if orig_img: va.ImageClip = orig_img
         if orig_audio: va.AudioFileClip = orig_audio
         if orig_concat: va.concatenate_videoclips = orig_concat

def test_assemble_video_no_scenes():
    """Test that it returns None if no scenes provided."""
    assembler = VideoAssembler()
    result = assembler.assemble_video([], "output.mp4")
    assert result is None

def test_assemble_video_mock_mode(tmp_path):
    """Test mock assembly creates a file."""
    # Force mock mode
    with patch('ai_novel_to_video.services.video_assembler.MOVIEPY_AVAILABLE', False):
        assembler = VideoAssembler()
        output_file = tmp_path / "test_video.mp4"
        scenes = [{'image': 'img.png', 'audio': 'audio.mp3'}]
        
        result = assembler.assemble_video(scenes, str(output_file))
        
        assert result == str(output_file)
        assert os.path.exists(output_file)
        with open(output_file, 'r') as f:
            assert "Mock Video File" in f.read()

def test_assemble_video_success(mock_moviepy, tmp_path):
    """Test successful video assembly with mocked moviepy."""
    mock_img_cls, mock_audio_cls, mock_concat = mock_moviepy
    
    # Setup mocks
    mock_audio_instance = MagicMock()
    mock_audio_instance.duration = 5
    mock_audio_cls.return_value = mock_audio_instance
    
    mock_img_instance = MagicMock()
    mock_img_cls.return_value = mock_img_instance
    mock_img_instance.set_duration.return_value = mock_img_instance
    mock_img_instance.set_audio.return_value = mock_img_instance
    
    mock_final_video = MagicMock()
    mock_concat.return_value = mock_final_video
    
    assembler = VideoAssembler()
    output_file = tmp_path / "final_video.mp4"
    
    # Create dummy files so existence check passes
    img_path = tmp_path / "img.png"
    img_path.touch()
    audio_path = tmp_path / "audio.mp3"
    audio_path.touch()
    
    scenes = [{'image': str(img_path), 'audio': str(audio_path)}]
    
    result = assembler.assemble_video(scenes, str(output_file))
    
    # Verify interactions
    mock_audio_cls.assert_called_with(str(audio_path))
    mock_img_cls.assert_called_with(str(img_path))
    mock_concat.assert_called_once()
    mock_final_video.write_videofile.assert_called_with(str(output_file), fps=24, codec='libx264', audio_codec='aac')
    
    assert result == str(output_file)

def test_assemble_video_missing_files(mock_moviepy, tmp_path):
    """Test that missing files are skipped."""
    mock_img_cls, mock_audio_cls, mock_concat = mock_moviepy
    
    assembler = VideoAssembler()
    output_file = tmp_path / "final_video.mp4"
    
    # Scene with non-existent files
    scenes = [{'image': 'non_existent.png', 'audio': 'non_existent.mp3'}]
    
    result = assembler.assemble_video(scenes, str(output_file))
    
    # Should return None because no valid clips were created
    assert result is None
    mock_concat.assert_not_called()

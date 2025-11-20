import pytest
import os
from unittest.mock import MagicMock, patch
from ai_novel_to_video.services.animation_service import AnimationService

# Mock moviepy to avoid actual rendering during unit tests
@pytest.fixture
def mock_moviepy():
    with patch('ai_novel_to_video.services.animation_service.ImageClip') as mock_image_clip:
        yield mock_image_clip

def test_init():
    service = AnimationService()
    assert service is not None

def test_apply_ken_burns_mock_mode():
    """Test behavior when MoviePy is not available."""
    with patch('ai_novel_to_video.services.animation_service.MOVIEPY_AVAILABLE', False):
        service = AnimationService()
        result = service.apply_ken_burns("dummy.png", 5.0)
        assert result is None

@patch('ai_novel_to_video.services.animation_service.MOVIEPY_AVAILABLE', True)
def test_apply_ken_burns_success(mock_moviepy):
    """Test successful application of Ken Burns effect."""
    service = AnimationService()
    
    # Setup mock clip
    mock_clip = MagicMock()
    # Ensure size is treated as a tuple, not a mock
    mock_clip.size = (1920, 1080)
    # Ensure methods return self (fluent interface)
    mock_clip.with_duration.return_value = mock_clip
    mock_clip.resized.return_value = mock_clip
    mock_clip.cropped.return_value = mock_clip
    mock_clip.with_updated_frame_function.return_value = mock_clip
    
    # Setup ImageClip constructor to return our mock_clip
    mock_moviepy.return_value = mock_clip
    
    # Test Zoom In
    result = service.apply_ken_burns("dummy.png", 5.0, direction='in')
    
    assert result == mock_clip
    mock_moviepy.assert_called_with("dummy.png")
    mock_clip.with_duration.assert_called_with(5.0)
    mock_clip.resized.assert_called() # Should be called for zoom
    mock_clip.cropped.assert_called() # Zoom in uses cropped
    
    # Test Panning (Left)
    # Reset mocks
    mock_clip.reset_mock()
    mock_clip.size = (1920, 1080) # Resetting might clear attributes? No, but good to be safe.
    mock_clip.with_duration.return_value = mock_clip
    mock_clip.resized.return_value = mock_clip
    mock_clip.with_updated_frame_function.return_value = mock_clip
    
    result = service.apply_ken_burns("dummy.png", 5.0, direction='left')
    
    assert result == mock_clip
    mock_clip.resized.assert_called() # Should be called to enlarge
    mock_clip.with_updated_frame_function.assert_called() # Panning uses this now
    
def test_apply_ken_burns_error_handling(mock_moviepy):
    """Test fallback when an exception occurs."""
    service = AnimationService()
    
    mock_clip = MagicMock()
    mock_clip.with_duration.return_value = mock_clip
    
    # Setup ImageClip to return mock_clip
    mock_moviepy.return_value = mock_clip
    
    # Make resized raise an exception
    mock_clip.resized.side_effect = Exception("Processing Error")
    
    result = service.apply_ken_burns("dummy.png", 5.0, direction='in')
    
    assert result is not None
    # Should be the fallback clip
    assert result == mock_clip

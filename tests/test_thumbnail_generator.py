import pytest
import os
from unittest.mock import MagicMock, patch
from PIL import Image
from ai_novel_to_video.services.thumbnail_generator import ThumbnailGenerator

@pytest.fixture
def mock_image_generator():
    return MagicMock()

def test_generate_thumbnail_success(mock_image_generator, tmp_path):
    """Test successful thumbnail generation."""
    generator = ThumbnailGenerator(mock_image_generator)
    
    # Create a dummy background image
    bg_path = tmp_path / "bg.png"
    img = Image.new('RGB', (100, 100), color='red')
    img.save(bg_path)
    
    # Mock image generator to return this path
    mock_image_generator.generate_image.return_value = str(bg_path)
    
    output_path = tmp_path / "thumbnail.png"
    
    result = generator.generate_thumbnail("Test Title", "Test Prompt", str(output_path))
    
    # Verify calls
    mock_image_generator.generate_image.assert_called_with("Test Prompt", str(output_path).replace(".png", "_bg.png"))
    
    assert result == str(output_path)
    assert os.path.exists(output_path)
    
    # Check if temp file was deleted
    assert not os.path.exists(str(output_path).replace(".png", "_bg.png"))

def test_generate_thumbnail_bg_failure(mock_image_generator, tmp_path):
    """Test failure when background image generation fails."""
    generator = ThumbnailGenerator(mock_image_generator)
    
    # Mock failure
    mock_image_generator.generate_image.return_value = None
    
    output_path = tmp_path / "thumbnail.png"
    result = generator.generate_thumbnail("Title", "Prompt", str(output_path))
    
    assert result is None
    assert not os.path.exists(output_path)

import pytest
import os
from unittest.mock import MagicMock, patch
from ai_novel_to_video.services.image_generator import ImageGenerator

@pytest.fixture
def mock_vertex_ai():
    with patch('ai_novel_to_video.services.image_generator.vertexai') as mock:
        yield mock

@pytest.fixture
def mock_image_model():
    with patch('ai_novel_to_video.services.image_generator.ImageGenerationModel') as mock:
        yield mock

def test_init_mock_mode_no_project():
    """Test initialization falls back to mock mode if no project ID."""
    with patch.dict(os.environ, {}, clear=True):
        generator = ImageGenerator(project_id=None)
        assert generator.model is None

def test_init_vertex_ai(mock_vertex_ai, mock_image_model):
    """Test initialization with Vertex AI."""
    generator = ImageGenerator(project_id="test-project")
    mock_vertex_ai.init.assert_called_with(project="test-project", location="us-central1")
    mock_image_model.from_pretrained.assert_called_with("imagegeneration@006")
    assert generator.model is not None

def test_generate_image_mock(tmp_path):
    """Test mock generation creates a file."""
    generator = ImageGenerator(project_id=None)
    output_file = tmp_path / "test_image.png"
    
    # Ensure PIL is mocked or handled if not present, but the service handles it.
    # We'll just check if file is created.
    result = generator.generate_image("A test prompt", str(output_file))
    
    assert result == str(output_file)
    assert os.path.exists(output_file)

def test_generate_image_vertex_success(mock_vertex_ai, mock_image_model, tmp_path):
    """Test Vertex AI generation success path."""
    generator = ImageGenerator(project_id="test-project")
    
    # Mock the model response
    mock_response_image = MagicMock()
    mock_image_model.from_pretrained.return_value.generate_images.return_value = [mock_response_image]
    
    output_file = tmp_path / "vertex_image.png"
    result = generator.generate_image("A cinematic scene", str(output_file))
    
    mock_response_image.save.assert_called_once()
    assert result == str(output_file)

def test_generate_image_vertex_failure_fallback(mock_vertex_ai, mock_image_model, tmp_path):
    """Test fallback to mock if Vertex AI fails."""
    generator = ImageGenerator(project_id="test-project")
    
    # Mock failure
    mock_image_model.from_pretrained.return_value.generate_images.side_effect = Exception("API Error")
    
    output_file = tmp_path / "fallback_image.png"
    result = generator.generate_image("A cinematic scene", str(output_file))
    
    assert result == str(output_file)
    assert os.path.exists(output_file)

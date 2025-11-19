import pytest
import os
from unittest.mock import MagicMock, patch, ANY
from ai_novel_to_video.services.youtube_uploader import YouTubeUploader

@pytest.fixture
def mock_google_api():
    with patch('ai_novel_to_video.services.youtube_uploader.build') as mock_build, \
         patch('ai_novel_to_video.services.youtube_uploader.MediaFileUpload') as mock_media:
        yield mock_build

def test_upload_video_mock_mode(tmp_path):
    """Test upload in mock mode (no client_secrets)."""
    uploader = YouTubeUploader(client_secrets_file="non_existent.json")
    
    video_path = tmp_path / "video.mp4"
    video_path.touch()
    
    video_id = uploader.upload_video(str(video_path), "Title", "Desc", ["tag"])
    
    assert video_id == "MOCK_VIDEO_ID_123"

def test_upload_video_success(mock_google_api, tmp_path):
    """Test successful upload structure."""
    # Setup mock service
    mock_service = MagicMock()
    mock_google_api.return_value = mock_service
    
    # Mock insert request
    mock_request = MagicMock()
    mock_service.videos().insert.return_value = mock_request
    
    # Mock response with progress and final ID
    mock_status = MagicMock()
    mock_status.progress.return_value = 1.0
    mock_request.next_chunk.side_effect = [(mock_status, {'id': 'REAL_VIDEO_ID'})]
    
    # Mock auth
    with patch('os.path.exists', return_value=True), \
         patch('pickle.load', return_value=MagicMock(valid=True)), \
         patch('builtins.open', new_callable=MagicMock) as mock_open:
        
        uploader = YouTubeUploader(client_secrets_file="secrets.json")
        
        video_path = tmp_path / "video.mp4"
        video_path.touch()
        
        video_id = uploader.upload_video(str(video_path), "Title", "Desc", ["tag"])
        
        assert video_id == 'REAL_VIDEO_ID'
        mock_service.videos().insert.assert_called()

def test_upload_video_with_thumbnail(mock_google_api, tmp_path):
    """Test upload with thumbnail."""
    mock_service = MagicMock()
    mock_google_api.return_value = mock_service
    
    # Mock insert response
    mock_request = MagicMock()
    mock_service.videos().insert.return_value = mock_request
    mock_request.next_chunk.return_value = (None, {'id': 'VID_123'})
    
    with patch('os.path.exists', return_value=True), \
         patch('pickle.load', return_value=MagicMock(valid=True)), \
         patch('builtins.open', new_callable=MagicMock) as mock_open:
        
        uploader = YouTubeUploader(client_secrets_file="secrets.json")
        
        video_path = tmp_path / "video.mp4"
        video_path.touch()
        thumb_path = tmp_path / "thumb.png"
        thumb_path.touch()
        
        uploader.upload_video(str(video_path), "Title", "Desc", [], str(thumb_path))
        
        mock_service.thumbnails().set.assert_called_with(
            videoId='VID_123',
            media_body=ANY
        )

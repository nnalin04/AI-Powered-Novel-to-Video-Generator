import pytest
from unittest.mock import MagicMock, patch
import json
from ai_novel_to_video.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_generate_stream_text_input(client):
    # Mock the pipeline to avoid actual processing
    with patch('ai_novel_to_video.app.pipeline') as mock_pipeline:
        # Setup mock to simulate progress callbacks
        def mock_process(input_type, input_data, video_type, callback):
            callback("Step 1", 25)
            callback("Step 2", 50)
            callback("Step 3", 75)
            return "Success"
        
        mock_pipeline.process_request.side_effect = mock_process

        # Send request
        response = client.post('/generate', data={
            'input_type': 'text',
            'text_input': 'Test story',
            'video_type': 'short'
        })

        # Verify response is a stream
        assert response.status_code == 200
        assert response.mimetype == 'text/event-stream'

        # Read stream content
        content = response.get_data(as_text=True)
        lines = content.split('\n\n')
        
        # Filter empty lines
        events = [line for line in lines if line.strip()]
        
        # Verify we got events
        assert len(events) >= 3
        
        # Parse first event (Start)
        data1 = json.loads(events[0].replace('data: ', ''))
        assert 'message' in data1
        
        # Parse progress events
        found_step_1 = False
        found_done = False
        
        for event in events:
            if not event.startswith('data: '):
                continue
            
            json_str = event.replace('data: ', '')
            try:
                data = json.loads(json_str)
                if data.get('message') == 'Step 1' and data.get('percent') == 25:
                    found_step_1 = True
                if data.get('done') and data.get('percent') == 100:
                    found_done = True
            except:
                pass
        
        assert found_step_1
        assert found_done

def test_generate_stream_error_handling(client):
    with patch('ai_novel_to_video.app.pipeline') as mock_pipeline:
        # Simulate error
        def mock_error(*args):
            raise Exception("Pipeline Failed")
        
        mock_pipeline.process_request.side_effect = mock_error

        response = client.post('/generate', data={
            'input_type': 'text',
            'text_input': 'Test',
            'video_type': 'short'
        })

        content = response.get_data(as_text=True)
        assert "Pipeline Failed" in content
        assert '"error": "Pipeline Failed"' in content

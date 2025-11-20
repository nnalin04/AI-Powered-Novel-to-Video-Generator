from flask import Flask, render_template, request, Response, stream_with_context
import os
import queue
import threading
import json
import time
from ai_novel_to_video.processing.pipeline import VideoGenerationPipeline
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize Pipeline
pipeline = VideoGenerationPipeline()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    # Extract form data
    input_type = request.form.get('input_type')
    video_type = request.form.get('video_type')
    
    input_data = {}
    if input_type == 'text':
        input_data['text_input'] = request.form.get('text_input')
    elif input_type == 'url':
        input_data['url_input'] = request.form.get('url_input')
    elif input_type == 'pdf':
        if 'pdf_file' in request.files:
            pdf_file = request.files['pdf_file']
            if pdf_file.filename:
                # Save file synchronously to avoid thread issues
                input_dir = 'ai_novel_to_video/input'
                os.makedirs(input_dir, exist_ok=True)
                filepath = os.path.join(input_dir, pdf_file.filename)
                pdf_file.save(filepath)
                input_data['pdf_path'] = filepath

    # Queue for communication between thread and generator
    msg_queue = queue.Queue()

    def progress_callback(message, percent):
        msg_queue.put({'message': message, 'percent': percent})

    def run_pipeline():
        try:
            # Run the pipeline
            result = pipeline.process_request(input_type, input_data, video_type, progress_callback)
            # Send final success message
            msg_queue.put({'message': result, 'percent': 100, 'done': True})
        except Exception as e:
            # Send error message
            msg_queue.put({'error': str(e), 'percent': 100, 'done': True})
        finally:
            # Signal end of stream
            msg_queue.put(None)

    # Start pipeline in a separate thread
    thread = threading.Thread(target=run_pipeline)
    thread.start()

    def generate_stream():
        # Yield initial message
        yield f"data: {json.dumps({'message': 'Starting generation...', 'percent': 0})}\n\n"
        
        while True:
            item = msg_queue.get()
            if item is None:
                break
            
            yield f"data: {json.dumps(item)}\n\n"
            
            if item.get('done'):
                break
    
    return Response(stream_with_context(generate_stream()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
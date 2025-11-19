```python
from flask import Flask, render_template, request
import os
from ai_novel_to_video.processing.pipeline import VideoGenerationPipeline
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize Pipeline
pipeline = VideoGenerationPipeline()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            print(f"Error processing request: {e}")
            return f"Error: {e}"

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
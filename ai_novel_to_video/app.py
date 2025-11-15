from flask import Flask, render_template, request
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file upload and mode selection
        input_type = request.form['input_type']
        video_type = request.form['video_type']

        if input_type == 'text':
            text_input = request.form['text_input']
            # Process text input
            print(f"Text Input: {text_input}")
            segments = segment_text(text_input)
            print(f"Segments: {segments}")
            screenplays = []
            for segment in segments:
                screenplay = paragraph_to_screenplay(segment)
                screenplays.append(screenplay)
                print(f"Screenplay: {screenplay}")
            print(f"Screenplays: {screenplays}")
        elif input_type == 'pdf':
            pdf_file = request.files['pdf_file']
            if pdf_file:
                # Save the uploaded PDF file
                pdf_file.save(os.path.join('ai_novel_to_video/input', pdf_file.filename))
                print(f"Uploaded PDF: {pdf_file.filename}")
                # TODO: Implement PDF processing
        elif input_type == 'url':
            url_input = request.form['url_input']
            print(f"URL Input: {url_input}")
            # TODO: Implement URL scraping
            try:
                import requests
                from bs4 import BeautifulSoup
                response = requests.get(url_input)
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                soup = BeautifulSoup(response.content, 'html.parser')
                # Extract all text from the webpage
                text = ' '.join(soup.stripped_strings)
                print(f"Extracted Text: {text}")
                segments = segment_text(text)
                print(f"Segments: {segments}")
                screenplays = [paragraph_to_screenplay(segment) for segment in segments]
                print(f"Screenplays: {screenplays}")
            except requests.exceptions.RequestException as e:
                print(f"Error fetching URL: {e}")
                text = f"Error fetching URL: {e}"

        print(f"Video Type: {video_type}")

        # TODO: Start the AI generation pipeline

        return "Video generation started! Check the console for the screenplay outputs."

    return render_template('index.html')

import google.generativeai as genai
import os

def paragraph_to_screenplay(paragraph):
    """Converts a paragraph into a screenplay object using Gemini API."""
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-pro')

    prompt = f"""Convert the following paragraph into a detailed cinematic screenplay object:
    {paragraph}

    The screenplay object should include:
    - scene_description: A detailed cinematic scene description
    - dialogues: A list of dialogues, with each dialogue including the character and the line
    - voiceover_text: Narration text for TTS

    The output should be a JSON object with the following structure:
    {{
      "scene_description": "Detailed cinematic scene description",
      "dialogues": [
        {{
          "character": "A",
          "line": "..."
        }},
        {{
          "character": "B",
          "line": "..."
        }}
      ],
      "voiceover_text": "Narration text for TTS"
    }}
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating screenplay: {e}"

def segment_text(text, word_count=150):
    """Segments the text into paragraphs or scenes based on the specified word count."""
    sentences = text.split('.')
    segments = []
    current_segment = ""
    current_word_count = 0

    for sentence in sentences:
        words = sentence.split()
        word_count_in_sentence = len(words)

        if current_word_count + word_count_in_sentence <= word_count:
            current_segment += sentence + "."
            current_word_count += word_count_in_sentence
        else:
            if current_segment:
                segments.append(current_segment.strip())
            current_segment = sentence + "."
            current_word_count = word_count_in_sentence

    if current_segment:
        segments.append(current_segment.strip())

    return segments

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
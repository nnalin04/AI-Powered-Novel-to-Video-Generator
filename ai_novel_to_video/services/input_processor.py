import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
import os

class InputProcessor:
    def __init__(self):
        pass

    def segment_text(self, text, word_count=150):
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

    def extract_text_from_url(self, url):
        """Extracts text from a given URL."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            text = ' '.join(soup.stripped_strings)
            return text
        except Exception as e:
            raise Exception(f"Error fetching URL: {e}")

    def extract_text_from_pdf(self, pdf_path):
        """Extracts text from a PDF file."""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {e}")

import os
from ai_novel_to_video.services.input_processor import InputProcessor

# Create a dummy PDF for testing if it doesn't exist
pdf_path = 'ai_novel_to_video/input/test.pdf'

# Initialize processor
processor = InputProcessor()

try:
    print(f"Attempting to extract text from: {pdf_path}")
    text = processor.extract_text_from_pdf(pdf_path)
    print("--- Extracted Text Start ---")
    print(text[:500]) # Print first 500 chars
    print("--- Extracted Text End ---")
    
    segments = processor.segment_text(text)
    print(f"Successfully segmented into {len(segments)} parts.")
    
except Exception as e:
    print(f"Verification Failed: {e}")

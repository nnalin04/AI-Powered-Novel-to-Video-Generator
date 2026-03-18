import vertexai
from vertexai.generative_models import GenerativeModel
import json
import os

creds_path = '/Users/nishitnalinsrivastava/dev/AI Agent/AI-Powered Novel-to-Video Generator/secrets/vertex-service-key.json'
with open(creds_path, 'r') as f:
    creds = json.load(f)
    project_id = creds.get('project_id')

vertexai.init(project=project_id, location='us-central1')

print("Testing gemini-2.5-pro...")
try:
    model = GenerativeModel('gemini-2.5-pro')
    # Use generate_content_async if available or just generate_content
    # Note: Vertex SDK in 2026 might have different methods but let's try standard ones
    response = model.generate_content('hi')
    print("SUCCESS: gemini-2.5-pro is available.")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"FAILURE: gemini-2.5-pro not found: {e}")

print("\nTesting gemini-2.0-pro-exp (as fallback)...")
try:
    model = GenerativeModel('gemini-2.0-pro-exp-02-05')
    response = model.generate_content('hi')
    print("SUCCESS: gemini-2.0-pro-exp is available.")
except Exception as e:
    print(f"FAILURE: gemini-2.0-pro-exp not found: {e}")

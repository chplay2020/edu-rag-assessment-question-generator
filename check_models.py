import os
import sys
from google import genai
from google.genai.errors import APIError

key = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
client = genai.Client(api_key=key)

try:
    print("Listing models:")
    for m in client.models.list():
        print(m.name)
except Exception as e:
    print(f"Error: {e}")

import os
import sys
from google import genai
from google.genai.errors import APIError

key = "AQ.Ab8RN6LUj9BtiKXTX-zXdHLttZWQBRWSj0-jSD4zz83M7v25Ww"
client = genai.Client(api_key=key)

try:
    print("Listing models:")
    for m in client.models.list():
        print(m.name)
except Exception as e:
    print(f"Error: {e}")

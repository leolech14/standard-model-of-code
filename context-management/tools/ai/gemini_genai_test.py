#!/usr/bin/env python3
"""Test using google-genai package with Vertex AI backend"""
from google import genai
from google.genai.types import HttpOptions

# Use Vertex AI backend (not API key)
client = genai.Client(
    vertexai=True,
    project="elements-archive-2026", 
    location="us-central1"
)

response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents="What is 2+2? Reply with just the number."
)
print(response.text)

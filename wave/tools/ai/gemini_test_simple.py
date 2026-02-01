#!/usr/bin/env python3
"""Simple Gemini test using Google AI SDK"""
import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(project="elements-archive-2026", location="us-central1")
model = GenerativeModel("gemini-2.0-flash-001")  # Try newer model

response = model.generate_content("Hello! What is 2+2?")
print(response.text)

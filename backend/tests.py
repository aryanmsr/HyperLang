import requests
import json

# Base URL where your FastAPI server is running.
BASE_URL = "http://127.0.0.1:8000"

# Example payload to test the endpoints.
payload = {
    "scenario": "A tourist enters a busy cafe and asks for advice on what to order.",
    "country_name": "Colombia"
}

# Test the generate_transcript endpoint.
transcript_response = requests.post(
    f"{BASE_URL}/generate_transcript",
    headers={"Content-Type": "application/json"},
    data=json.dumps(payload)
)
print("----- Transcript Endpoint Response -----")
print(transcript_response.status_code)
print(transcript_response.json())

# Test the generate_explained_transcript endpoint.
explained_response = requests.post(
    f"{BASE_URL}/generate_explained_transcript",
    headers={"Content-Type": "application/json"},
    data=json.dumps(payload)
)
print("----- Explained Transcript Endpoint Response -----")
print(explained_response.status_code)
print(explained_response.json())

# Test the generate_audio endpoint.
audio_response = requests.post(
    f"{BASE_URL}/generate_audio",
    headers={"Content-Type": "application/json"},
    data=json.dumps(payload)
)
print("----- Generate Audio Endpoint Response -----")
print(audio_response.status_code)
print(audio_response.json())

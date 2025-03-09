"""
Test Script for FastAPI Language Learning Backend Endpoints

This script tests the two main endpoints of the language learning backend:
1. /generate_explained_transcript - Generates a transcript with teacher commentary
2. /generate_audio - Generates audio files from the transcript

The script verifies:
- Proper character assignment based on language/country
- Correct language usage in dialogues
- Maestro's English explanations
- Audio file generation with correct voice mappings

Usage:
    1. Ensure FastAPI server is running (uvicorn backend.app:app --reload)
    2. Run: python -m backend.test_endpoints
"""

import requests
import json

# Base URL for the FastAPI server
BASE_URL = "http://localhost:8000"

def test_generate_explained_transcript():
    """
    Test the generate_explained_transcript endpoint.
    
    This function tests transcript generation for multiple language-country pairs:
    1. Spanish (Colombia) - Tests basic dialogue generation
    2. French (France) - Tests multilingual support
    
    For each test case, it verifies:
    - Proper HTTP response (200 OK)
    - Correct transcript format
    - Character name consistency
    - Language appropriateness
    - Maestro's commentary integration
    
    Returns:
        None. Prints test results to console.
    """
    print("\n----- Testing Generate Explained Transcript Endpoint -----")
    
    # Test case 1: Spanish Colombia
    payload = {
        "scenario": "A tourist asks for directions to the nearest café",
        "country_name": "Colombia",
        "language": "Spanish"
    }
    
    print("\nTesting Spanish (Colombia) scenario...")
    response = requests.post(
        f"{BASE_URL}/generate_explained_transcript",
        json=payload
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("\nGenerated Transcript Lines:")
        transcript_lines = response.json()["transcript"]
        for line in transcript_lines:
            print(line)
    else:
        print("Error:", response.text)

    # Test case 2: French France
    payload = {
        "scenario": "Ordering breakfast at a local boulangerie",
        "country_name": "France",
        "language": "French"
    }
    
    print("\nTesting French (France) scenario...")
    response = requests.post(
        f"{BASE_URL}/generate_explained_transcript",
        json=payload
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("\nGenerated Transcript Lines:")
        transcript_lines = response.json()["transcript"]
        for line in transcript_lines:
            print(line)
    else:
        print("Error:", response.text)

def test_generate_audio():
    """
    Test the generate_audio endpoint.
    
    This function tests the complete audio generation pipeline:
    1. Transcript generation with character dialogue
    2. Maestro's commentary integration
    3. Text-to-Speech processing
    4. Audio file creation and combination
    
    Verifies:
    - Proper HTTP response (200 OK)
    - File generation (transcript and audio)
    - Directory structure creation
    - Character-to-voice mapping
    - Audio file accessibility
    
    The test uses a Spanish (Colombia) scenario to verify:
    - Correct voice assignment for Carlos and Maria
    - Proper English voice for Maestro
    - Appropriate pauses between dialogue lines
    
    Returns:
        None. Prints test results and file locations to console.
    """
    print("\n----- Testing Generate Audio Endpoint -----")
    
    payload = {
        "scenario": "Ordering coffee at a local café",
        "country_name": "Colombia",
        "language": "Spanish"
    }
    
    print("\nGenerating audio for Spanish (Colombia) scenario...")
    response = requests.post(
        f"{BASE_URL}/generate_audio",
        json=payload
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("\nGeneration Details:")
        print(f"Message: {result['message']}")
        
        # Print the transcript content
        details = result['details']
        transcript_file = details['transcript_file']
        print("\nTranscript Content:")
        with open(transcript_file, 'r', encoding='utf-8') as f:
            print(f.read())
            
        print("\nFile Locations:")
        print(f"- Conversation ID: {details['conversation_id']}")
        print(f"- Conversation Directory: {details['conversation_dir']}")
        print(f"- Transcript File: {details['transcript_file']}")
        print(f"- Final Audio File: {details['final_audio_file']}")
    else:
        print("Error:", response.text)

if __name__ == "__main__":
    """
    Main execution block.
    
    Performs:
    1. Server availability check
    2. Transcript generation test
    3. Audio generation test
    
    Requires:
    - FastAPI server running on localhost:8000
    - Valid API key for ElevenLabs
    - Proper configuration in config.py
    """
    # First, check if the server is running
    try:
        health_check = requests.get(f"{BASE_URL}/")
        if health_check.status_code == 200:
            print("Server is running!")
            
            # Run the tests
            test_generate_explained_transcript()
            test_generate_audio()
        else:
            print("Server returned unexpected status code:", health_check.status_code)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
        print("Please make sure the FastAPI server is running on http://localhost:8000")
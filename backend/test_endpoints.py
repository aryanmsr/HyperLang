import requests
import json

# Base URL for the FastAPI server
BASE_URL = "http://localhost:8000"

def test_generate_explained_transcript():
    """Test the generate_explained_transcript endpoint"""
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
    """Test the generate_audio endpoint"""
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
        print("\nFile Locations:")
        details = result['details']
        print(f"- Conversation ID: {details['conversation_id']}")
        print(f"- Conversation Directory: {details['conversation_dir']}")
        print(f"- Transcript File: {details['transcript_file']}")
        print(f"- Final Audio File: {details['final_audio_file']}")
    else:
        print("Error:", response.text)

if __name__ == "__main__":
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
# HyperLang AI

HyperLang AI is a language learning app that uses large language models (LLMs) to generate personalized dialogues and convert them into realistic audio output via Text-to-Speech (TTS).

---

## Milestone 1: Backend Prototype

### Goal:
Build a backend that simulates conversations between AI agents in **Spanish** and **French** about _"what love really means"_ (lol) and generates corresponding TTS output.

---

## Who is this for?
- For us, our friends, our parents, and even Aryan's girlfriend's mom.

---

## Features:
- **AI Dialogue Generation:** Simulate multilingual conversations between two agents, with a third agent providing explanations or translations.
- **Text-to-Speech (TTS):** Generate realistic voice output with appropriate accents and emotion.

---

## Tech Stack:
- **Backend:** FastAPI
- **LLM:** Mistral 7B Instruct
- **TTS:** Flash v2.5 (ElevenLabs)

---

## Usage:

### 1. Setup:
- **Install Dependencies:**
  ```bash
  pip install -r requirements.txt
  ```

- **Configure Environment:** 
Create a `.env` file in the project root with your API keys:
  ```bash
  ELEVEN_API_KEY = 'your_elevenlabs_api_key'
  HUGGINGFACE_TOKEN = 'your_huggingface_token'
  ```

### 2. Running the Backend:
- **Start the FastAPI server from the project root:**
  ```bash
  uvicorn app.app:app --reload
  ```

### 3. Endpoints:
- `/generate_transcript`: Generates a raw dialogue transcript.
- `/generate_explained_transcript`: Generates a transcript with teacher commentary and translation
- `/generate_audio`: Runs the full pipeline (transcript generation, TTS processing) and saves outputs (transcript and audio files) in a uniquely named folder under `data/conversations/`.

### 4. Testing:
- **Swagger UI**: Navigate to http://127.0.0.1:8000/docs to interact with the API endpoints.
- **cURL Commands:**: Use cURL to test endpoints.
- **Jupyter Notebook**: Use the provided `tts_experiments_v3_elevenlabs.ipynb` notebooks to test individual modules and track output at each step.

### 5. Output:
Each conversation generates a unique folder under `data/conversations/` containing:
- `transcript.txt` – The generated dialogue transcript.
- Individual audio files (e.g., `line_1.mp3`, `line_1.wav`, etc.).
- `final_conversation.wav` – The combined audio file for the entire conversation.

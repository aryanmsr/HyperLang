from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend import config
from backend.modelClasses import PromptHandler, LLMWrapper, TeacherAgent
from backend.pipeline import run_pipeline
from backend.utils import reformat_transcript_to_list 

app = FastAPI()

# Enable CORS for frontend requests (e.g., from a Next.js frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranscriptRequest(BaseModel):
    """
    Request model for generating explained transcripts and audio.
    
    Attributes:
        scenario (str): The scenario text for which a transcript is generated.
        country_name (str): The country name used in prompt formatting (default: "Colombia").
        language (str): The target language for the conversation (default: "Spanish").
    """
    scenario: str
    country_name: str = "Colombia"
    language: str = "Spanish"

class TranscriptResponse(BaseModel):
    """
    Response model containing the generated explained transcript.
    
    Attributes:
        transcript (str): The explained transcript with teacher commentary.
    """
    transcript: str

class AudioResponse(BaseModel):
    """
    Response model for audio generation.
    
    Attributes:
        message (str): Status message.
        details (dict): Details about the generated conversation outputs (e.g., conversation folder, transcript file, and audio file paths).
    """
    message: str
    details: dict

@app.get("/")
async def root():
    """
    Root endpoint returning a welcome message.
    
    Returns:
        dict: A dictionary with a welcome message.
    """
    return {"message": "Hello World from FastAPI"}

@app.post("/generate_explained_transcript", response_model=TranscriptResponse)
async def generate_explained_transcript_endpoint(request: TranscriptRequest):
    """
    Generate an explained transcript with teacher commentary.
    
    This endpoint uses the system prompt template to generate a raw transcript based on the given
    scenario, country, and language, then applies the teacher prompt template (via TeacherAgent) to add 
    English commentary and translations while preserving the original dialogue.
    
    Args:
        request (TranscriptRequest): The request body containing scenario, country_name, and language.
    
    Returns:
        dict: A dictionary containing the explained transcript.
    """
    prompt_handler = PromptHandler(config.SYSTEM_PROMPT_TEMPLATE_PATH)
    transcript_generator = LLMWrapper(model_name=config.MODEL_NAME)
    teacher_agent = TeacherAgent(
        template_path=config.TEACHER_PROMPT_TEMPLATE_PATH,
        model_name=config.MODEL_NAME,
        temperature=0.2,
    )
    
    # Format the system prompt with scenario, country, and language.
    prompt = prompt_handler.format_prompt(
        scenario=request.scenario,
        country_name=request.country_name,
        language=request.language
    )
    raw_transcript = transcript_generator.generate(prompt)
    print(raw_transcript)
    
    explained_transcript = teacher_agent.explain(
        raw_transcript,
        scenario=request.scenario,
        country_name=request.country_name,
        language=request.language
    )
    print(explained_transcript)
    
    return {"transcript": explained_transcript}

@app.post("/generate_audio", response_model=AudioResponse)
async def generate_audio_endpoint(request: TranscriptRequest):
    """
    Generate audio from an explained transcript.
    
    This endpoint runs the full pipeline to generate a raw transcript, produce an explained transcript,
    reformat the explained transcript into a list of lines using a utility function, and then convert 
    the transcript to audio using TTS. The outputs (transcript and audio files) are saved in a uniquely 
    named conversation folder.
    
    Args:
        request (TranscriptRequest): The request body containing scenario, country_name, and language.
    
    Returns:
        dict: A dictionary containing a status message and details about the generated outputs.
    """
    result = run_pipeline(
        scenario=request.scenario,
        country_name=request.country_name,
        language=request.language
    )
    
    transcript_file = result.get("transcript_file")
    with open(transcript_file, "r", encoding="utf-8") as f:
        explained_transcript = f.read()

    transcript_lines = reformat_transcript_to_list(explained_transcript)
    print("----- Reformat Transcript Lines -----")
    print(transcript_lines)
    
    result["transcript_lines"] = transcript_lines
    return {"message": "Audio generated", "details": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)

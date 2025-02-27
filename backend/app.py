from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend import config
from backend.modelClasses import PromptHandler, TranscriptGenerator, TeacherAgent
from backend.pipeline import run_pipeline

app = FastAPI()

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranscriptRequest(BaseModel):
    """
    Request model for transcript generation endpoints.

    Attributes:
        scenario (str): The scenario text for which a transcript is to be generated.
        country_name (str): The country name used in prompt formatting (default: "Colombia").
    """
    scenario: str
    country_name: str = "Colombia"

class TranscriptResponse(BaseModel):
    """
    Response model for transcript generation endpoints.

    Attributes:
        transcript (str): The generated transcript.
    """
    transcript: str

@app.get("/")
async def root():
    """
    Root endpoint returning a welcome message.
    
    Returns:
        dict: A dictionary with a welcome message.
    """
    return {"message": "Hello World from FastAPI"}

@app.post("/generate_transcript", response_model=TranscriptResponse)
async def generate_transcript_endpoint(request: TranscriptRequest):
    """
    Generate a raw transcript based on the given scenario and country.
    
    This endpoint uses the system prompt template to generate a dialogue transcript via an LLM.
    
    Args:
        request (TranscriptRequest): The request body containing scenario and country_name.
    
    Returns:
        dict: A dictionary containing the generated transcript.
    """
    prompt_handler = PromptHandler(config.SYSTEM_PROMPT_TEMPLATE_PATH)
    transcript_generator = TranscriptGenerator(model_name=config.MODEL_NAME)
    prompt = prompt_handler.format_prompt_scenario(
        request.scenario, country_name=request.country_name
    )
    transcript = transcript_generator.generate_transcript(prompt)
    print(transcript)
    return {"transcript": transcript}

@app.post("/generate_explained_transcript", response_model=TranscriptResponse)
async def generate_explained_transcript_endpoint(request: TranscriptRequest):
    """
    Generate an explained transcript with teacher commentary.
    
    This endpoint uses both the system prompt and teacher prompt templates to generate a transcript
    that includes dialogue and teacher explanations.
    
    Args:
        request (TranscriptRequest): The request body containing scenario and country_name.
    
    Returns:
        dict: A dictionary containing the explained transcript.
    """
    prompt_handler = PromptHandler(config.SYSTEM_PROMPT_TEMPLATE_PATH)
    transcript_generator = TranscriptGenerator(model_name=config.MODEL_NAME)
    teacher_agent = TeacherAgent(
        template_path=config.TEACHER_PROMPT_TEMPLATE_PATH,
        model_name=config.MODEL_NAME,
        temperature=0.2,
    )
    prompt = prompt_handler.format_prompt_scenario(
        request.scenario, country_name=request.country_name
    )
    transcript = transcript_generator.generate_transcript(prompt)
    explained_transcript = teacher_agent.explain_transcript(
        transcript, request.scenario, request.country_name
    )
    print(explained_transcript)
    return {"transcript": explained_transcript}

@app.post("/generate_audio")
async def generate_audio_endpoint(request: TranscriptRequest):
    """
    Generate audio files from a generated transcript.
    
    This endpoint runs the full pipeline which includes transcript generation, reformatting,
    and TTS processing. The outputs (transcript and audio files) are saved in a uniquely
    named conversation folder.
    
    Args:
        request (TranscriptRequest): The request body containing scenario and country_name.
    
    Returns:
        dict: A dictionary containing a message and details about the generated conversation outputs.
    """
    result = run_pipeline(request.scenario, country_name=request.country_name)
    return {"message": "Audio generated", "details": result}

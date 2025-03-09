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
    Response model containing the formatted transcript lines.
    
    Attributes:
        transcript (list): List of formatted transcript lines.
    """
    transcript: list

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
    Returns the transcript as a formatted list of lines.
    """
    # Get character information from config
    characters = config.CHARACTER_CONFIG[request.language][request.country_name]
    character_1 = characters["speaker_1"]
    character_2 = characters["speaker_2"]
    
    # Generate raw transcript
    prompt_handler = PromptHandler(config.SYSTEM_PROMPT_TEMPLATE_PATH)
    transcript_generator = LLMWrapper(model_name=config.MODEL_NAME)
    
    prompt = prompt_handler.format_prompt(
        scenario=request.scenario,
        country_name=request.country_name,
        language=request.language,
        character_1_name=character_1["name"],
        character_2_name=character_2["name"]
    )
    raw_transcript = transcript_generator.generate(prompt)
    
    # Generate explained transcript
    teacher_agent = TeacherAgent(
        template_path=config.TEACHER_PROMPT_TEMPLATE_PATH,
        model_name=config.MODEL_NAME,
        temperature=0.2,
    )
    
    explained_transcript = teacher_agent.explain(
        raw_transcript,
        scenario=request.scenario,
        country_name=request.country_name,
        language=request.language,
        character_1_name=character_1["name"],
        character_2_name=character_2["name"]
    )
    
    # Format into lines
    transcript_lines = reformat_transcript_to_list(explained_transcript)
    
    return {"transcript": transcript_lines}  # Return the formatted list

@app.post("/generate_audio", response_model=AudioResponse)
async def generate_audio_endpoint(request: TranscriptRequest):
    """
    Generate audio using the full pipeline.
    """
    # Simply use run_pipeline which handles everything
    result = run_pipeline(
        scenario=request.scenario,
        country_name=request.country_name,
        language=request.language
    )
    
    return {
        "message": "Audio generated successfully",
        "details": result
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from backend import config
from backend.modelClasses import PromptHandler, LLMWrapper, TeacherAgent
from backend.pipeline import run_pipeline
from backend.utils import reformat_transcript_to_list 

app = FastAPI()

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranscriptRequest(BaseModel):
    """Request model for generating transcripts and audio"""
    scenario: str
    country_name: str = "Colombia"
    language: str = "Spanish"
    local_storage: bool = config.USE_LOCAL_STORAGE 

class TranscriptResponse(BaseModel):
    """Response model containing the formatted transcript lines"""
    transcript: List[str]

class AudioResponse(BaseModel):
    """Response model for audio generation details"""
    message: str
    details: dict

@app.get("/")
async def root():
    return {"message": "Hello World from FastAPI"}

@app.post("/generate_explained_transcript", response_model=TranscriptResponse)
async def generate_explained_transcript_endpoint(request: TranscriptRequest):
    """
    Generate an explained transcript with teacher commentary.
    Returns the transcript as a formatted list of lines.
    """
    # Get character information from config
    characters = config.CHARACTER_CONFIG[request.language][request.country_name]
    print("----- Characters -----")
    print(characters)

    character_1 = characters["speaker_1"]
    character_2 = characters["speaker_2"]

    # Generate raw transcript
    prompt_handler = PromptHandler(config.SYSTEM_PROMPT_TEMPLATE_PATH)
    transcript_generator = LLMWrapper(model_name=config.MODEL_NAME)
    
    # Format prompt with character names
    prompt = prompt_handler.format_prompt(
        scenario=request.scenario,
        country_name=request.country_name,
        language=request.language,
        character_1_name=character_1["name"],
        character_2_name=character_2["name"]
    )
    
    # Generate initial transcript
    raw_transcript = transcript_generator.generate(prompt)
    print("----- Raw Transcript -----")
    print(raw_transcript)
    
    # Generate explained transcript with Maestro's commentary
    teacher_agent = TeacherAgent(
        template_path=config.TEACHER_PROMPT_TEMPLATE_PATH,
        model_name=config.MODEL_NAME,
        temperature=0.0,
    )
    
    explained_transcript = teacher_agent.explain(
        raw_transcript,
        scenario=request.scenario,
        country_name=request.country_name,
        language=request.language,
        character_1_name=character_1["name"],
        character_2_name=character_2["name"]
    )
    print("----- Explained Transcript -----")
    print(explained_transcript)
    
    # Format into lines
    transcript_lines = reformat_transcript_to_list(explained_transcript)
    print("----- Formatted Lines -----")
    print(transcript_lines)
    
    return {"transcript": transcript_lines}

@app.post("/generate_audio", response_model=AudioResponse)
async def generate_audio_endpoint(request: TranscriptRequest):
    """
    Generate audio using the full pipeline.
    Returns details about the generated files.
    """
    result = run_pipeline(
        scenario=request.scenario,
        country_name=request.country_name,
        language=request.language,
        local_storage=request.local_storage  
    )
    
    return {
        "message": "Audio generated successfully",
        "details": result
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
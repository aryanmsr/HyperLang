# app.py
from fastapi import FastAPI
from pydantic import BaseModel
import config
from app.modelClasses import PromptHandler, TranscriptGenerator, TeacherAgent

app = FastAPI()

# Define request and response models
class TranscriptRequest(BaseModel):
    scenario: str
    country_name: str = "Spain"

class TranscriptResponse(BaseModel):
    transcript: str

# Initialize your classes
prompt_handler = PromptHandler(config.PROMPT_TEMPLATE_PATH)
transcript_generator = TranscriptGenerator(model_name=config.MODEL_NAME)
teacher_agent = TeacherAgent(
    template_path=config.TEACHER_TEMPLATE_PATH,
    model_name=config.MODEL_NAME,
    temperature=0.2
)

@app.post("/generate_transcript", response_model=TranscriptResponse)
async def generate_transcript(request: TranscriptRequest):
    prompt = prompt_handler.format_prompt_scenario(request.scenario, country_name=request.country_name)
    transcript = transcript_generator.generate_transcript(prompt)
    print(transcript)
    return {"transcript": transcript}

@app.post("/generate_explained_transcript", response_model=TranscriptResponse)
async def generate_transcript(request: TranscriptRequest):
    prompt = prompt_handler.format_prompt_scenario(request.scenario, country_name=request.country_name)
    transcript = transcript_generator.generate_transcript(prompt)
    explained_transcript = teacher_agent.explain_transcript(transcript, request.scenario, request.country_name)
    print(explained_transcript)
    return {"transcript": explained_transcript}



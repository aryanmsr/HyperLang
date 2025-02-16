from fastapi import FastAPI
from pydantic import BaseModel
from app import config
from app.modelClasses import PromptHandler, TranscriptGenerator, TeacherAgent
from app.pipeline import run_pipeline

app = FastAPI()

class TranscriptRequest(BaseModel):
    scenario: str
    country_name: str = "Colombia"


class TranscriptResponse(BaseModel):
    transcript: str


@app.post("/generate_transcript", response_model=TranscriptResponse)
async def generate_transcript_endpoint(request: TranscriptRequest):
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
    result = run_pipeline(request.scenario, country_name=request.country_name)
    return {"message": "Audio generated", "details": result}

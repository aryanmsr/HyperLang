"""
Includes prompt handler, transcript generator, and teacher agent classes.
"""

import os
import asyncio
import config
from typing import Any, AsyncGenerator
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
load_dotenv()


class PromptHandler:
    """
    Loads and formats prompt templates from a file.
    """

    def __init__(self, template_path: str) -> None:
        self.template_path = template_path

    def load_prompt(self) -> str:
        with open(self.template_path, 'r', encoding='utf-8') as file:
            return file.read()

    def format_prompt_scenario(self, scenario: str, country_name: str = "Spain") -> str:
        template = self.load_prompt()
        return template.format(
            scenario=scenario,
            country_name=country_name
        )

    def format_prompt(self, **kwargs) -> str:
        template = self.load_prompt()
        return template.format(**kwargs)

class TranscriptGenerator:
    """
    Generates or streams text from a Hugging Face model.
    """

    def __init__(self, model_name: str, temperature: float = 0.7) -> None:
        self.client = InferenceClient(api_key=os.getenv('HUGGINGFACE_TOKEN'))
        self.model_name = model_name
        self.temperature = temperature

    def generate_transcript(self, prompt: str) -> str:
        try:
            messages = [{"role": "user", "content": prompt}]
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=10000
            )
            return completion.choices[0].message.content
        except Exception as exc:
            return f"Error: {str(exc)}"

    async def generate_transcript_stream(
        self, prompt: str
    ) -> AsyncGenerator[str, None]:
        try:
            messages = [{"role": "user", "content": prompt}]
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=10000,
                stream=True
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
                    await asyncio.sleep(0.01)
        except Exception as exc:
            yield f"Error: {str(exc)}"


class TeacherAgent:
    """
    Uses a teacher-specific prompt to provide annotated explanations or translations.
    """

    def __init__(
        self,
        template_path: str,
        model_name: str,
        temperature: float = 0.7
    ) -> None:
        self.prompt_handler = PromptHandler(template_path)
        self.transcript_generator = TranscriptGenerator(
            model_name=model_name,
            temperature=temperature
        )

    def explain_transcript(
        self,
        transcript: str,
        scenario: str,
        country_name: str = "Spain"
    ) -> str:
        teacher_prompt = self.prompt_handler.format_prompt(
            transcript=transcript,
            scenario=scenario,
            country_name=country_name
        )
        return self.transcript_generator.generate_transcript(teacher_prompt)

    async def explain_transcript_stream(
        self,
        transcript: str,
        scenario: str,
        country_name: str = "Spain"
    ) -> AsyncGenerator[str, None]:
        teacher_prompt = self.prompt_handler.format_prompt(
            transcript=transcript,
            scenario=scenario,
            country_name=country_name
        )
        async for chunk in self.transcript_generator.generate_transcript_stream(teacher_prompt):
            yield chunk
"""
Includes a flexible LLM wrapper, prompt handler, and teacher agent classes.
"""

import os
import asyncio
from typing import AsyncGenerator
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()


class PromptHandler:
    """
    Loads and formats prompt templates from a file.
    """

    def __init__(self, template_path: str) -> None:
        """
        Initialize the PromptHandler with the path to a prompt template file.

        Args:
            template_path (str): Path to the prompt template file.
        """
        self.template_path = template_path

    def load_template(self) -> str:
        """
        Load the prompt template from the file.

        Returns:
            str: The prompt template.
        """
        with open(self.template_path, "r", encoding="utf-8") as file:
            return file.read()

    def format_prompt(self, **kwargs) -> str:
        """
        Format the loaded prompt template with the given keyword arguments.

        Args:
            **kwargs: Keyword arguments to format the template.

        Returns:
            str: The formatted prompt.
        """
        template = self.load_template()
        return template.format(**kwargs)


class LLMWrapper:
    """
    A flexible wrapper around Huggingface Inference Client that generates text given any prompt.
    """

    def __init__(self, model_name: str, temperature: float = 0.7) -> None:
        """
        Initialize the LLMWrapper with a model name and temperature.

        Args:
            model_name (str): The name or identifier of the LLM model.
            temperature (float): The sampling temperature (default 0.7).
        """
        self.client = InferenceClient(api_key=os.getenv("HUGGINGFACE_TOKEN"))
        self.model_name = model_name
        self.temperature = temperature

    def generate(self, prompt: str) -> str:
        """
        Generate text from the LLM using the provided prompt.

        Args:
            prompt (str): The prompt to send to the LLM.

        Returns:
            str: The generated text or an error message if something fails.
        """
        try:
            messages = [{"role": "user", "content": prompt}]
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=10000,
            )
            return completion.choices[0].message.content
        except Exception as exc:
            return f"Error: {str(exc)}"

    async def generate_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """
        Generate text from the LLM in a streaming fashion.

        Args:
            prompt (str): The prompt to send to the LLM.

        Yields:
            str: Chunks of generated text.
        """
        try:
            messages = [{"role": "user", "content": prompt}]
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=10000,
                stream=True,
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
    Uses a teacher-specific prompt template to generate annotated explanations or translations.
    Leverages PromptHandler for formatting and LLMWrapper for text generation.
    """

    def __init__(self, template_path: str, model_name: str, temperature: float = 0.7) -> None:
        """
        Initialize the TeacherAgent with a teacher prompt template, model name, and temperature.

        Args:
            template_path (str): Path to the teacher prompt template.
            model_name (str): The name or identifier of the LLM model.
            temperature (float): The sampling temperature (default 0.7).
        """
        self.prompt_handler = PromptHandler(template_path)
        self.llm = LLMWrapper(model_name, temperature)

    def explain(self, transcript: str, **kwargs) -> str:
        """
        Generate an explanation or translation based on the provided transcript and additional context.

        Args:
            transcript (str): The base transcript to be explained.
            **kwargs: Additional keyword arguments (e.g., scenario, country_name) to format the prompt.

        Returns:
            str: The generated explanation or translation.
        """
        prompt = self.prompt_handler.format_prompt(transcript=transcript, **kwargs)
        return self.llm.generate(prompt)

    async def explain_stream(self, transcript: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        Generate explanations or translations in a streaming fashion.

        Args:
            transcript (str): The base transcript to be explained.
            **kwargs: Additional keyword arguments (e.g., scenario, country_name) to format the prompt.

        Yields:
            str: Chunks of generated explanation text.
        """
        prompt = self.prompt_handler.format_prompt(transcript=transcript, **kwargs)
        async for chunk in self.llm.generate_stream(prompt):
            yield chunk

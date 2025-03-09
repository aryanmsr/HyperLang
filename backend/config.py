import os
from dotenv import load_dotenv

load_dotenv()

# Prompt templates
SYSTEM_PROMPT_TEMPLATE_PATH = "./backend/prompts/system_prompt_template.txt"
TEACHER_PROMPT_TEMPLATE_PATH = "./backend/prompts/teacher_prompt_template.txt"

# Example scenario file (e.g., cafe conversation)
SCENARIO_CAFE_PATH = "./backend/prompts/scenarios/cafe.txt"

# LLM configuration
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"

# ElevenLabs configuration for TTS
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
TTS_MODEL_ID = "eleven_flash_v2_5"

# Audio file settings
GENERATED_OUTPUT_DIR = "./data/conversations"
PAUSE_DURATION_MS = 800



CHARACTER_CONFIG = {
    "maestro": {
        "name": "Maestro",
        "gender": "male",
        "language": "English",
        "voice_id": "JBFqnCBsd6RMkjVDRZzb"  # Fixed English voice for Maestro
    },
    "Spanish": {
        "Colombia": {
            "speaker_1": {
                "name": "Carlos",
                "gender": "male",
                "language": "Spanish",
                "country": "Colombia",
                "voice_id": "sdxJtmxpzgSLekrYUGIu"
            },
            "speaker_2": {
                "name": "Maria",
                "gender": "female",
                "language": "Spanish",
                "country": "Colombia",
                "voice_id": "86V9x9hrQds83qf7zaGn"
            }
        },
        "Spain": {
            "speaker_1": {
                "name": "Antonio",
                "gender": "male",
                "language": "Spanish",
                "country": "Spain",
                "voice_id": "wB2lj4ZqL876iV5QQ5KK"
            },
            "speaker_2": {
                "name": "Isabel",
                "gender": "female",
                "language": "Spanish",
                "country": "Spain",
                "voice_id": "RgXx32WYOGrd7gFNifSf"
            }
        }
    },
    "French": {
        "France": {
            "speaker_1": {
                "name": "Charles",
                "gender": "male",
                "language": "French",
                "country": "France",
                "voice_id": "hv6gVog5LgtIUX88Nmq8"
            },
            "speaker_2": {
                "name": "Sophie",
                "gender": "female",
                "language": "French",
                "country": "France",
                "voice_id": "pVsdIxxCbRrbiwOhiRwg"
            }
        }
    }
}


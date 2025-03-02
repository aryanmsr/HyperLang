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



VOICE_CONFIG = {
    "English": {
        "default": {
            "default": "JBFqnCBsd6RMkjVDRZzb", 
        }
    },

    "French": {
        "France": {
            "male": [
                "hv6gVog5LgtIUX88Nmq8"
            ],
            "female": [
                "pVsdIxxCbRrbiwOhiRwg"
            ]
        }
    },

    "Spanish": {
        "Colombia": {
            "male": [
                "J2Jb9yZNvpXUNAL3a2bw"
            ],
            "female": [
                "86V9x9hrQds83qf7zaGn"
            ]
        },
        "Spain": {
            "male": [
                "wB2lj4ZqL876iV5QQ5KK"
            ],
            "female": [
                "RgXx32WYOGrd7gFNifSf"
            ]
        }
    }
}


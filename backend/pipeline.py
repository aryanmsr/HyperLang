## NEED TO FIX. Transcript should be formatted in a very specific way in the pipeline.
import os
import datetime
import config
from backend.modelClasses import PromptHandler, TranscriptGenerator
from backend.tts import TTSProcessor


def load_scenario(scenario_file_path: str) -> str:
    """
    Load scenario details from a file.
    """
    with open(scenario_file_path, "r", encoding="utf-8") as file:
        return file.read()



def format_transcript(transcript: str) -> list:
    """
    Split the transcript into non-empty, stripped lines,
    ignoring lines that are just header separators (e.g., "-----").
    """
    lines = [line.strip() for line in transcript.splitlines() if line.strip()]
    filtered_lines = [line for line in lines if not line.startswith("-----")]
    return filtered_lines


def run_pipeline(scenario: str, country_name: str = "Colombia") -> dict:
    """
    Given a scenario and country name, generate a transcript using the system prompt,
    then process it into audio and save all outputs in a unique conversation folder.
    """
    unique_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    conversation_dir = os.path.join(config.GENERATED_OUTPUT_DIR, unique_id)
    os.makedirs(conversation_dir, exist_ok=True)

    final_audio_file = os.path.join(conversation_dir, "final_conversation.wav")
    transcript_file = os.path.join(conversation_dir, "transcript.txt")

    prompt_handler = PromptHandler(config.SYSTEM_PROMPT_TEMPLATE_PATH)
    transcript_generator = TranscriptGenerator(config.MODEL_NAME)
    prompt = prompt_handler.format_prompt_scenario(scenario, country_name=country_name)
    transcript = transcript_generator.generate_transcript(prompt)
    print("Generated Transcript:")
    print(transcript)

    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write(transcript)

    transcript_lines = format_transcript(transcript) #TODO
    tts_processor = TTSProcessor(api_key=config.ELEVEN_API_KEY)
    tts_processor.process_transcript(
        transcript_lines,
        speaker_voices=config.SPEAKER_VOICES,
        output_dir=conversation_dir,
        final_audio_file=final_audio_file,
    )

    return {
        "conversation_id": unique_id,
        "conversation_dir": conversation_dir,
        "transcript_file": transcript_file,
        "final_audio_file": final_audio_file,
    }


if __name__ == "__main__":

    scenario_text = load_scenario(config.SCENARIO_CAFE_PATH)

    output = run_pipeline(scenario_text, country_name="Colombia")

    print("Pipeline complete:", output)

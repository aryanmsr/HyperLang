import os
import datetime
from backend import config
from backend.modelClasses import PromptHandler, LLMWrapper, TeacherAgent
from backend.tts import TTSProcessor
from backend.utils import reformat_transcript_to_list

def load_scenario(scenario_file_path: str) -> str:
    """
    Load scenario details from a file.
    
    Args:
        scenario_file_path (str): Path to the scenario file.
    
    Returns:
        str: The scenario text.
    """
    with open(scenario_file_path, "r", encoding="utf-8") as file:
        return file.read()

def run_pipeline(scenario: str, country_name: str = "Colombia", language: str = "Spanish") -> dict:
    """
    Given a scenario, country name, and language, generate a transcript using the system prompt,
    then process it into audio and save all outputs in a unique conversation folder.
    
    The system prompt template is formatted with {scenario}, {country_name}, {language}, and character names.
    The resulting transcript is then reformatted into a list of lines before passing to the TTS module.
    
    Args:
        scenario (str): The scenario text.
        country_name (str): The country name used in prompt formatting.
        language (str): The target language for the conversation.
    
    Returns:
        dict: Details of the generated conversation outputs.
    """
    unique_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    conversation_dir = os.path.join(config.GENERATED_OUTPUT_DIR, unique_id)
    os.makedirs(conversation_dir, exist_ok=True)
    
    final_audio_file = os.path.join(conversation_dir, "final_conversation.wav")
    transcript_file = os.path.join(conversation_dir, "transcript.txt")
    
    # Get character information from config
    characters = config.CHARACTER_CONFIG[language][country_name]
    character_1 = characters["speaker_1"]
    character_2 = characters["speaker_2"]
    
    # Generate raw transcript using the system prompt template with character names
    prompt_handler = PromptHandler(config.SYSTEM_PROMPT_TEMPLATE_PATH)
    transcript_generator = LLMWrapper(config.MODEL_NAME)
    prompt = prompt_handler.format_prompt(
        scenario=scenario,
        country_name=country_name,
        language=language,
        character_1_name=character_1["name"],
        character_2_name=character_2["name"]
    )
    raw_transcript = transcript_generator.generate(prompt)
    print("----- Generated Transcript -----")
    print(raw_transcript)

    # Create the teacher agent instance
    teacher_agent = TeacherAgent(
        template_path=config.TEACHER_PROMPT_TEMPLATE_PATH,
        model_name=config.MODEL_NAME,
        temperature=0.0,
    )

    # Generate the explained transcript using keyword arguments for additional context
    explained_transcript = teacher_agent.explain(
        raw_transcript, 
        scenario=scenario, 
        country_name=country_name,
        language=language,
        character_1_name=character_1["name"],
        character_2_name=character_2["name"]
    )

    print("----- Explained Transcript -----")
    print(explained_transcript)
    
    # Save the transcript to a file.
    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write(explained_transcript)
    
    # Reformat the transcript into a list of lines for TTS processing.
    transcript_lines = reformat_transcript_to_list(explained_transcript)
    print("----- Transcript Lines for TTS -----")
    print(transcript_lines)
    
    # Process transcript into audio files using TTSProcessor.
    tts_processor = TTSProcessor(api_key=config.ELEVEN_API_KEY)
    tts_processor.process_transcript(
        transcript_lines,
        output_dir=conversation_dir,
        final_audio_file=final_audio_file,
        language=language,
        country=country_name,
        characters=characters  # Pass character config to TTS processor
    )
    return {
        "conversation_id": unique_id,
        "conversation_dir": conversation_dir,
        "transcript_file": transcript_file,
        "final_audio_file": final_audio_file,
    }

if __name__ == "__main__":
    scenario_text = load_scenario(config.SCENARIO_CAFE_PATH)
    output = run_pipeline(scenario_text, country_name="Colombia", language="Spanish")
    print("Pipeline complete:", output)

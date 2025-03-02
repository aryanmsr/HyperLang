import json
from backend import config
from backend.modelClasses import LLMWrapper




def infer_speaker_genders(transcript: str) -> dict:
    """
    Uses the LLM to infer the gender for each speaker in the transcript.
    
    The transcript is expected to be a string with dialogue lines formatted as "Speaker: Speech".
    This function sends a prompt to the LLM asking it to return a JSON object mapping each speaker
    to either "male" or "female". If the LLM output cannot be parsed, it returns an empty dict.
    
    Args:
        transcript (str): The explained transcript text.
    
    Returns:
        dict: A dictionary mapping speaker names to "male" or "female".
    """
    prompt = (
        "Given the following transcript, identify each speaker and determine their gender (male or female). "
        "Return a JSON object where each key is a speaker name and each value is either 'male' or 'female'. "
        "Note that Maestro is ALWAYS a male."
        "Do not include any extra text.\n\nTranscript:\n" + transcript
    )

    llm = LLMWrapper(config.MODEL_NAME, temperature=0.0)
    output = llm.generate(prompt)
    try:
        mapping = json.loads(output)
        for k, v in mapping.items():
            if v not in ["male", "female"]:
                raise ValueError(f"Invalid gender '{v}' for speaker '{k}'.")
        return mapping
    except Exception as e:
        print("Error inferring speaker genders:", e)
        return {}
    

def reformat_transcript_to_list(transcript: str) -> list:
    """
    Reformat the explained transcript into a list of lines.

    This function splits the transcript by newline, trims each line,
    and removes lines that consist solely of hyphens (used as separators).
    It preserves all other content, including dialogue, Maestro interjections,
    and the lesson summary.

    Args:
        transcript (str): The explained transcript text.

    Returns:
        list: A list of transcript lines.
    """
    lines = transcript.splitlines()
    formatted = []
    for line in lines:
        stripped = line.strip()
        if not stripped or all(ch == '-' for ch in stripped):
            continue
        formatted.append(stripped)
    return formatted

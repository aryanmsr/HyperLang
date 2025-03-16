import boto3
import json
import os
from backend import config
from backend.modelClasses import LLMWrapper
from dotenv import load_dotenv

load_dotenv()

aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
aws_default_region = os.environ.get('AWS_DEFAULT_REGION')

session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_default_region
)

s3_client = session.client('s3')


def upload_to_s3(file_path, bucket_name, s3_key):
    """
    Upload a file to an S3 bucket.

    Args:
        file_path (str): The local path to the file to upload.
        bucket_name (str): The name of the S3 bucket.
        s3_key (str): The S3 key (path) where the file will be stored.
    """
    try:
        s3_client.upload_file(file_path, bucket_name, s3_key)
        print(f"Uploaded {file_path} to s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print(f"Failed to upload {file_path} to S3: {e}")

def download_from_s3(bucket_name, s3_key, download_path):
    """
    Download a file from an S3 bucket.

    Args:
        bucket_name (str): The name of the S3 bucket.
        s3_key (str): The S3 key (path) of the file to download.
        download_path (str): The local path where the file will be saved.
    """
    try:
        s3_client.download_file(bucket_name, s3_key, download_path)
        print(f"Downloaded s3://{bucket_name}/{s3_key} to {download_path}")
    except Exception as e:
        print(f"Failed to download {s3_key} from S3: {e}")


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

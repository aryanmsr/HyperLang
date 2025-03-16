import os
import re
from pydub import AudioSegment
from elevenlabs import ElevenLabs, save
from dotenv import load_dotenv
from backend import config
from backend.utils import infer_speaker_genders, upload_to_s3

load_dotenv()

class TTSProcessor:
    """
    Processes a transcript by synthesizing audio for each line,
    converting to WAV, and combining them into a final audio file.
    """

    def __init__(
        self,
        api_key: str,
        model_id: str = config.TTS_MODEL_ID,
        pause_duration_ms: int = config.PAUSE_DURATION_MS,
    ) -> None:
        self.api_key = api_key
        self.model_id = model_id
        self.pause_duration_ms = pause_duration_ms
        self.client = ElevenLabs(api_key=self.api_key)

    def synthesize_speech(self, text: str, speaker_id: str, output_path: str) -> None:
        """
        Generate audio from text using ElevenLabs API and save it as an MP3 file.
        """
        audio = self.client.text_to_speech.convert(
            voice_id=speaker_id,
            output_format="mp3_44100_128",
            text=text,
            model_id=self.model_id,
        )
        save(audio, output_path)

    def convert_mp3_to_wav(self, mp3_path: str, wav_path: str) -> None:
        """
        Convert an MP3 file to WAV format using pydub.
        """
        audio = AudioSegment.from_mp3(mp3_path)
        audio.export(wav_path, format="wav")

    def combine_audio_files(self, input_dir: str, output_file: str) -> None:
        """
        Combine multiple WAV audio files with pauses in between.
        """
        audio_files = []
        for filename in os.listdir(input_dir):
            if filename.endswith(".wav") and filename.startswith("line_"):
                match = re.search(r"line_(\d+)", filename)
                if match:
                    index = int(match.group(1))
                    audio_files.append((index, os.path.join(input_dir, filename)))
                else:
                    print(f"Skipping unexpected file: {filename}")
        audio_files.sort(key=lambda x: x[0])
        pause = AudioSegment.silent(duration=self.pause_duration_ms)
        combined = AudioSegment.empty()
        for _, wav_file in audio_files:
            print(f"Adding {wav_file} to the combined audio...")
            segment = AudioSegment.from_wav(wav_file)
            combined += segment + pause
        if len(combined) > self.pause_duration_ms:
            combined = combined[:-self.pause_duration_ms]  # remove final pause
        combined.export(output_file, format="wav")
        print(f"Combined audio saved to {output_file}")

    def process_transcript(
        self, transcript_lines: list, output_dir: str, final_audio_file: str,
        language: str = "Spanish", country: str = "Colombia", characters: dict = None,
        local_storage: bool = config.USE_LOCAL_STORAGE
    ) -> None:
        """
        For each transcript line (formatted as 'Speaker: Speech'),
        synthesize audio, convert to WAV, and then combine all files.
        
        Uses fixed character configurations to map speakers to voices:
        - "Maestro" always uses the fixed English voice.
        - Other speakers are mapped directly to their configured voices.
        
        Args:
            transcript_lines (list): List of transcript lines.
            output_dir (str): Directory to save the individual audio files.
            final_audio_file (str): Path to the final combined audio file.
            language (str): The language of the conversation (e.g., "Spanish", "French").
            country (str): The country for voice mapping (e.g., "Colombia").
            characters (dict): Character configuration mapping speakers to voices.
            local_storage (bool): Flag to determine if outputs should be stored locally.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Get Maestro's fixed voice configuration
        maestro_config = config.CHARACTER_CONFIG["maestro"]
        
        for idx, line in enumerate(transcript_lines, start=1):
            if ": " not in line:
                print(f"Line {idx} is not in expected format: {line}")
                continue
            
            speaker, text = line.split(": ", 1)
            speaker = speaker.strip()
            text = text.strip()
            
            # Remove quotation marks if present
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1]
            
            # Get voice ID based on speaker
            if speaker in ["Maestro", "Key learning points", "Lesson Summary"]:
                speaker_id = maestro_config["voice_id"]
            else:
                for char_key, char_info in characters.items():
                    if char_info["name"] == speaker:
                        speaker_id = char_info["voice_id"]
                        break
                else:
                    print(f"No voice configuration found for speaker '{speaker}'. Skipping line {idx}.")
                    continue
            
            if not speaker_id:
                print(f"No speaker id found for '{speaker}'. Skipping line {idx}.")
                continue
            
            mp3_path = os.path.join(output_dir, f"line_{idx}.mp3")
            wav_path = os.path.join(output_dir, f"line_{idx}.wav")
            print(f"Synthesizing line {idx} for '{speaker}' using voice '{speaker_id}'...")
            self.synthesize_speech(text, speaker_id, mp3_path)
            self.convert_mp3_to_wav(mp3_path, wav_path)
            
            if not local_storage:
                s3_key_mp3 = f"outputs/{os.path.basename(output_dir)}/line_{idx}.mp3"
                s3_key_wav = f"outputs/{os.path.basename(output_dir)}/line_{idx}.wav"
                upload_to_s3(mp3_path, config.S3_BUCKET_NAME, s3_key_mp3)
                upload_to_s3(wav_path, config.S3_BUCKET_NAME, s3_key_wav)
        
        self.combine_audio_files(output_dir, final_audio_file)
        
        if not local_storage:
            s3_key_final = f"outputs/{os.path.basename(output_dir)}/final_conversation.wav"
            upload_to_s3(final_audio_file, config.S3_BUCKET_NAME, s3_key_final)
            
            # Delete local files after final upload
            for file_name in os.listdir(output_dir):
                file_path = os.path.join(output_dir, file_name)
                os.remove(file_path)
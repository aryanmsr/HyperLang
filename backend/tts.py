import os
import re
from pydub import AudioSegment
from elevenlabs import ElevenLabs, save
from dotenv import load_dotenv
from backend import config
from backend.utils import infer_speaker_genders

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
        language: str = "Spanish", country: str = "Colombia"
    ) -> None:
        """
        For each transcript line (formatted as 'Speaker: Speech'),
        synthesize audio, convert to WAV, and then combine all files.
        
        Dynamically assigns voices based on language, country, and inferred speaker gender:
          - "Maestro" and "Lesson Summary" always use the fixed English voice.
          - For all other speakers, if language is not English:
                Use voices from the {language} configuration.
                If a country-specific list exists, use it; otherwise, use the default for that language.
                The LLM is used to infer the gender of each speaker, and male speakers are assigned from the "male" list,
                while female speakers are assigned from the "female" list.
        
        Args:
            transcript_lines (list): List of transcript lines.
            output_dir (str): Directory to save the individual audio files.
            final_audio_file (str): Path to the final combined audio file.
            language (str): The language of the conversation (e.g., "Spanish", "French", "English").
            country (str): The country for voice mapping (e.g., "Colombia").
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Fixed voice for Maestro and Lesson Summary (always English).
        fixed_voice = config.VOICE_CONFIG["English"]["default"]["default"]
        
        # For non-English languages, look up the voice config.
        if language != "English":
            language_key = language.title()  # Ensure correct key, e.g., "Spanish" or "French".
            language_config = config.VOICE_CONFIG.get(language_key, config.VOICE_CONFIG["Spanish"])
            voice_config = language_config.get(country, language_config.get("default"))
        else:
            voice_config = config.VOICE_CONFIG["English"]["default"]
        
        available_male = list(voice_config.get("male", []))
        available_female = list(voice_config.get("female", []))
        
        # Infer speaker genders using LLM.
        full_transcript = "\n".join(transcript_lines)
        inferred_genders = infer_speaker_genders(full_transcript)
        print("Inferred speaker genders:", inferred_genders)
        
        assigned_voices = {}
        
        for idx, line in enumerate(transcript_lines, start=1):
            if ": " not in line:
                print(f"Line {idx} is not in expected format: {line}")
                continue
            
            speaker, text = line.split(": ", 1)
            speaker = speaker.strip()
            text = text.strip()
            
            if speaker in ["Maestro", "Lesson Summary"]:
                speaker_id = fixed_voice
            else:
                gender = inferred_genders.get(speaker)
                if not gender:
                    print(f"Gender not inferred for '{speaker}', skipping line {idx}.")
                    continue
                
                if speaker not in assigned_voices:
                    if gender.lower() == "male":
                        if available_male:
                            assigned_voices[speaker] = available_male.pop(0)
                        else:
                            # Fallback to default if available.
                            fallback = config.VOICE_CONFIG[language]["default"].get("male", [None])[0]
                            if fallback:
                                assigned_voices[speaker] = fallback
                            else:
                                print(f"No male voice available for '{speaker}'. Skipping line {idx}.")
                                continue
                    elif gender.lower() == "female":
                        if available_female:
                            assigned_voices[speaker] = available_female.pop(0)
                        else:
                            fallback = config.VOICE_CONFIG[language]["default"].get("female", [None])[0]
                            if fallback:
                                assigned_voices[speaker] = fallback
                            else:
                                print(f"No female voice available for '{speaker}'. Skipping line {idx}.")
                                continue
                    else:
                        print(f"Unknown gender '{gender}' for speaker '{speaker}'. Skipping line {idx}.")
                        continue
                speaker_id = assigned_voices[speaker]
            
            if not speaker_id:
                print(f"No speaker id found for '{speaker}'. Skipping line {idx}.")
                continue
            
            mp3_path = os.path.join(output_dir, f"line_{idx}.mp3")
            wav_path = os.path.join(output_dir, f"line_{idx}.wav")
            print(f"Synthesizing line {idx} for '{speaker}' using voice '{speaker_id}'...")
            self.synthesize_speech(text, speaker_id, mp3_path)
            self.convert_mp3_to_wav(mp3_path, wav_path)
        
        self.combine_audio_files(output_dir, final_audio_file)

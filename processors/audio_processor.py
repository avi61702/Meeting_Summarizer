import time
import os
import json
import assemblyai as aai

aai.settings.api_key = os.environ.get('ASSEMBLYAI_API_KEY', '2d96f4086a8b48b2a8fcb53c487f37a7')

def transcribe_audio(filepath: str) -> str:
    """
    Transcribes audio using AssemblyAI's API.
    """
    print(f"Transcribing audio file at {filepath} using AssemblyAI...")
    config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.universal)
    transcript = aai.Transcriber(config=config).transcribe(filepath)
    if transcript.status == "error":
        raise RuntimeError(f"Transcription failed: {transcript.error}")
    return transcript.text

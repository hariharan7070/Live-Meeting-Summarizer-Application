import whisper
import torch
from pyannote.audio import Pipeline
from pydub import AudioSegment

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token="HF_TOKEN"
)

audio_file = "sample.wav"

print("Running diarization...")
diarization = pipeline(audio_file)

print("Loading Whisper model...")
model = whisper.load_model("base")

audio = AudioSegment.from_wav(audio_file)

print("\nSpeaker-wise Transcription:\n")
 
for turn, _, speaker in diarization.itertracks(yield_label=True):
    start = int(turn.start * 1000)
    end = int(turn.end * 1000)

    segment = audio[start:end]
    segment.export("temp.wav", format="wav")

    result = model.transcribe("temp.wav")

    print(f"{speaker} ({turn.start:.1f}s - {turn.end:.1f}s):")
    print(result["text"])
    print("-" * 50)
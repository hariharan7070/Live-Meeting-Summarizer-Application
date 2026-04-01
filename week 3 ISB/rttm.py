from pyannote.audio import Pipeline

HF_TOKEN = "HF_TOKEN"

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=HF_TOKEN
)

audio_file = "sample.wav"

print("Running diarization...")
diarization = pipeline(audio_file)

with open("sample.rttm", "w") as f:
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        start = turn.start
        duration = turn.end - turn.start
        f.write(f"SPEAKER sample 1 {start:.2f} {duration:.2f} <NA> <NA> {speaker} <NA> <NA>\n")

print("RTTM file generated successfully.")
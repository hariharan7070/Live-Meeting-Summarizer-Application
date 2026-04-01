from pyannote.audio import Pipeline
from pyannote.metrics.diarization import DiarizationErrorRate
from pyannote.database.util import load_rttm

HF_TOKEN = "YOUR_HF_TOKEN"

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=HF_TOKEN
)

audio_file = "sample.wav"

print("Running diarization...")
hypothesis = pipeline(audio_file)

reference = load_rttm("sample.rttm")["sample"]

metric = DiarizationErrorRate()
der = metric(reference, hypothesis)

accuracy = (1 - der) * 100

print("\n===== DER REPORT =====")
print(f"Diarization Error Rate (DER): {der:.4f}")
print(f"Accuracy: {accuracy:.2f}%")

if der < 0.20:
    print("Requirement Achieved ✅ (DER < 20%)")
else:
    print("DER higher than 20% ❌")
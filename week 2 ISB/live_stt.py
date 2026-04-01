import pyaudio
import json
from vosk import Model, KaldiRecognizer

model = Model("vosk-model-small-en-us-0.15")
rec = KaldiRecognizer(model, 16000)

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=8000)

stream.start_stream()

print("Speak now... Press Ctrl+C to stop.\n")

transcription_log = ""

try:
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get("text", "")
            print("You said:", text)
            transcription_log += text + " "
except KeyboardInterrupt:
    print("\nStopping...")

with open("live_transcription.txt", "w") as f:
    f.write(transcription_log)

print("Transcription saved.")
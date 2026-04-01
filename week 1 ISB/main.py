
import whisper
print("Loading model...")
model = whisper.load_model("base")

print("Transcribing audio...")
result = model.transcribe('meeting.wav')

print("\nTranscription:\n")
print(result["text"])

with open("whisper_output.txt","w") as f:
    f.write(result["text"])

print("\n Saved transcription to whisper_output.txt")
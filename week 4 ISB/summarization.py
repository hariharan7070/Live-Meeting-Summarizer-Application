import whisper
from transformers import pipeline

audio_file = "meeting.wav"

print("Loading Whisper model...")
model = whisper.load_model("base")

print("Transcribing audio...")
result = model.transcribe(audio_file)

transcript = result["text"]

print("\n--- Generated Transcript ---\n")
print(transcript)

with open("transcript.txt", "w") as f:
    f.write(transcript)

print("\nLoading summarization model...")
summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)

print("Generating meeting summary...\n")

summary = summarizer(
    transcript,
    max_length=120,
    min_length=40,
    do_sample=False
)

summary_text = summary[0]["summary_text"]

print("\n--- Meeting Summary ---\n")
print(summary_text)

with open("summary.txt", "w") as f:
    f.write(summary_text)

print("\nTranscript saved to transcript.txt")
print("Summary saved to summary.txt")
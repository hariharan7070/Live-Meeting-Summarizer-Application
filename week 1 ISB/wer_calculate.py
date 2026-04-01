from jiwer import wer

# Read ground truth
with open("Original.txt", "r") as f:
    ground_truth = f.read().lower()

# Read Whisper output
with open("whisper_output.txt", "r") as f:
    whisper_text = f.read().lower()

# Read Vosk output
with open("vosk_output.txt", "r") as f:
    vosk_text = f.read().lower()

# Calculate WER
whisper_wer = wer(ground_truth, whisper_text)
vosk_wer = wer(ground_truth, vosk_text)

print("Whisper WER:", whisper_wer)
print("Vosk WER:", vosk_wer)

if whisper_wer < vosk_wer:
    print("Whisper model is better.")
else:
    print("Vosk model is better.")

from jiwer import wer

# Read Original Text
with open("Original.txt", "r") as f:
    ground_truth = f.read().lower()

# Read Live Transcription
with open("live_transcription.txt", "r") as f:
    predicted_text = f.read().lower()

# Calculate WER
error = wer(ground_truth, predicted_text)

print("Word Error Rate (WER):", error)

accuracy = (1 - error) * 100
print("Accuracy:", round(accuracy, 2), "%")

if error < 0.15:
    print("Requirement Achieved (WER < 15%)")
else:
    print(" WER is higher than 15%")
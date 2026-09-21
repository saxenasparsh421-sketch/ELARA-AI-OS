import json
import os
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models",
    "vosk-model-small-en-us-0.15"
)

SAMPLE_RATE = 16000

print("Loading Vosk model...")

model = Model(MODEL_PATH)

# Limit recognition to words/phrases useful for the wake word.
grammar = json.dumps([
    "elara",
    "alara",
    "ilara",
    "a lara",
    "hey elara",
    "a ladder",
    "a lotta",
    "lana",
    "a louder",
    "[unk]"
])

recognizer = KaldiRecognizer(
    model,
    SAMPLE_RATE,
    grammar
)

audio_queue = queue.Queue()


def callback(indata, frames, time_info, status):
    if status:
        print(status)

    audio_queue.put(bytes(indata))


print("Vosk loaded successfully.")
print()
print('Say "Elara"...')
print("Press Ctrl+C to stop.")
print()

with sd.RawInputStream(
    samplerate=SAMPLE_RATE,
    blocksize=4000,
    dtype="int16",
    channels=1,
    callback=callback,
):

    while True:

        data = audio_queue.get()

        if recognizer.AcceptWaveform(data):

            result = json.loads(recognizer.Result())

            text = result.get("text", "").lower().strip()

            if not text:
                continue

            print("Heard:", text)

            # Direct recognition
            if "elara" in text:
                print()
                print(">>> ELARA WAKE WORD DETECTED! <<<")
                print()

            # Common Vosk misrecognitions of "Elara"
            elif text in {
                "alara",
                "ilara",
                "a lara",
                "lana",
            }:
                print()
                print(">>> ELARA WAKE WORD DETECTED (variant)! <<<")
                print()

            # Keep these visible for now; DON'T trigger on them yet.
            elif text in {
                "a ladder",
                "a lotta",
                "a louder",
            }:
                print("Possible Elara misrecognition — NOT triggering.")
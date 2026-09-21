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
recognizer = KaldiRecognizer(model, SAMPLE_RATE)

audio_queue = queue.Queue()


def callback(indata, frames, time_info, status):
    if status:
        print(status)

    audio_queue.put(bytes(indata))


print("Vosk loaded successfully.")
print('Say "Elara"...')
print("Press Ctrl+C to stop.\n")


with sd.RawInputStream(
    samplerate=SAMPLE_RATE,
    blocksize=8000,
    dtype="int16",
    channels=1,
    callback=callback,
):

    while True:

        data = audio_queue.get()

        if recognizer.AcceptWaveform(data):

            result = json.loads(
                recognizer.Result()
            )

            text = result.get("text", "").lower().strip()

            if text:
                print("Heard:", text)

                if "elara" in text:
                    print("\n>>> ELARA WAKE WORD DETECTED! <<<\n")
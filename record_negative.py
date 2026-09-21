import sounddevice as sd
from scipy.io.wavfile import write
from pathlib import Path
import time

SAMPLE_RATE = 16000
DURATION = 1.5
TOTAL_SAMPLES = 20

OUTPUT_DIR = Path("wakeword_training") / "negative"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("\nELARA Negative Sample Recorder")
print("==============================")
print(f"Recording {TOTAL_SAMPLES} samples.")
print("In recordings mein 'Elara' MAT bolna.\n")

for i in range(1, TOTAL_SAMPLES + 1):
    input(f"Press ENTER for sample {i}/{TOTAL_SAMPLES}...")

    print("Get ready...")
    time.sleep(1)

    print("RECORDING — normal sentence bolo")
    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16"
    )
    sd.wait()

    filename = OUTPUT_DIR / f"negative_{i:03d}.wav"
    write(filename, SAMPLE_RATE, audio)

    print(f"Saved: {filename}\n")

print("================================")
print("20 negative samples recorded!")
print("================================")
import os
import glob
import wave
import numpy as np
import sounddevice as sd
from scipy.fftpack import dct


# ============================================================
# CONFIG
# ============================================================

SAMPLE_RATE = 16000
RECORD_SECONDS = 1.5

ELARA_FOLDER = os.path.join(
    os.path.dirname(__file__),
    "wakeword_training",
    "positive"
)

# Start conservative.
# We will tune this after testing.
THRESHOLD = 0.78


# ============================================================
# AUDIO LOADING
# ============================================================

def load_wav(path):
    with wave.open(path, "rb") as wf:
        rate = wf.getframerate()
        channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        frames = wf.readframes(wf.getnframes())

    if rate != SAMPLE_RATE:
        raise ValueError(f"{path}: expected 16000 Hz, got {rate}")

    if channels != 1:
        raise ValueError(f"{path}: expected mono")

    if sample_width != 2:
        raise ValueError(f"{path}: expected 16-bit audio")

    audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32)

    return audio / 32768.0


# ============================================================
# MFCC FEATURE EXTRACTION
# ============================================================

def hz_to_mel(hz):
    return 2595 * np.log10(1 + hz / 700)


def mel_to_hz(mel):
    return 700 * (10 ** (mel / 2595) - 1)


def mfcc(audio, sample_rate=16000, num_coeffs=13):

    # Pre-emphasis
    emphasized = np.append(
        audio[0],
        audio[1:] - 0.97 * audio[:-1]
    )

    # Frame settings
    frame_length = int(0.025 * sample_rate)
    frame_step = int(0.010 * sample_rate)

    num_frames = 1 + max(
        0,
        (len(emphasized) - frame_length) // frame_step
    )

    padded_length = (
        (num_frames - 1) * frame_step
        + frame_length
    )

    padded = np.pad(
        emphasized,
        (0, max(0, padded_length - len(emphasized))),
        mode="constant"
    )

    indices = (
        np.tile(
            np.arange(frame_length),
            (num_frames, 1)
        )
        +
        np.tile(
            np.arange(num_frames) * frame_step,
            (frame_length, 1)
        ).T
    )

    frames = padded[indices]

    # Hamming window
    frames *= np.hamming(frame_length)

    # FFT
    nfft = 512
    magnitude = np.absolute(
        np.fft.rfft(frames, nfft)
    )

    power = (
        1.0 / nfft
    ) * (magnitude ** 2)

    # Mel filterbank
    low_mel = hz_to_mel(300)
    high_mel = hz_to_mel(8000)

    mel_points = np.linspace(
        low_mel,
        high_mel,
        26
    )

    hz_points = mel_to_hz(mel_points)

    bins = np.floor(
        (nfft + 1) * hz_points / sample_rate
    ).astype(int)

    filterbank = np.zeros((24, nfft // 2 + 1))

    for m in range(1, 25):

        left = bins[m - 1]
        center = bins[m]
        right = bins[m + 1]

        for k in range(left, center):
            if center != left:
                filterbank[m - 1, k] = (
                    (k - left)
                    / (center - left)
                )

        for k in range(center, right):
            if right != center:
                filterbank[m - 1, k] = (
                    (right - k)
                    / (right - center)
                )

    filter_energies = np.dot(
        power,
        filterbank.T
    )

    filter_energies = np.maximum(
        filter_energies,
        1e-10
    )

    log_energy = np.log(filter_energies)

    coefficients = dct(
        log_energy,
        type=2,
        axis=1,
        norm="ortho"
    )[:, :num_coeffs]

    return coefficients


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_features(features):

    mean = np.mean(features, axis=0)
    std = np.std(features, axis=0) + 1e-8

    return (features - mean) / std


# ============================================================
# FEATURE DISTANCE
# ============================================================

def compare_features(a, b):

    # Make both the same number of frames
    frames = min(len(a), len(b))

    a = a[:frames]
    b = b[:frames]

    distance = np.mean(
        np.sqrt(
            np.sum(
                (a - b) ** 2,
                axis=1
            )
        )
    )

    return distance


# ============================================================
# BUILD ELARA TEMPLATES
# ============================================================

print("Loading Elara recordings...")

files = sorted(
    glob.glob(
        os.path.join(
            ELARA_FOLDER,
            "*.wav"
        )
    )
)

if not files:
    raise RuntimeError(
        "No Elara WAV recordings found."
    )

templates = []

for path in files:

    audio = load_wav(path)

    features = mfcc(audio)
    features = normalize_features(features)

    templates.append(features)

    print(
        "Loaded:",
        os.path.basename(path)
    )

print()
print(f"Loaded {len(templates)} Elara templates.")
print()


# ============================================================
# MICROPHONE
# ============================================================

def record_audio():

    print(
        f"Listening for {RECORD_SECONDS:.1f} seconds..."
    )

    recording = sd.rec(
        int(RECORD_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    return recording.flatten().astype(
        np.float32
    ) / 32768.0


# ============================================================
# DETECTION
# ============================================================

print("===================================")
print("       ELARA DETECTOR TEST")
print("===================================")
print()
print("Say: Elara")
print("Press Ctrl+C to stop.")
print()

while True:

    audio = record_audio()

    features = mfcc(audio)
    features = normalize_features(features)

    distances = []

    for template in templates:

        distance = compare_features(
            features,
            template
        )

        distances.append(distance)

    best_distance = min(distances)

    # Convert distance to a rough similarity score.
    similarity = 1.0 / (
        1.0 + best_distance
    )

    print(
        f"Similarity: {similarity:.3f}"
    )

    if similarity >= THRESHOLD:

        print()
        print(
            ">>> ELARA DETECTED! <<<"
        )
        print()

    else:

        print(
            "No wake word detected."
        )

    print()
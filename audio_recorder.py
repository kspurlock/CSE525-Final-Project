import pyaudio
import os
from tkinter import Tk, Button
import wave

# Constants
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
WAVE_OUTPUT_FILENAME = "audio_samples/sample_{}.wav"

# Create directory for audio_samples if it doesn't exist
if not os.path.exists("audio_samples"):
    os.makedirs("audio_samples")


def record_audio(record_seconds: int = 5) -> str:
    """Records audio and stores it in a WAV file

    Args:
        record_seconds (int, optional): the number of seconds to record for.
        Defaults to 5.

    Returns:
        str: filename of temporary WAV file
    """
    audio = pyaudio.PyAudio()

    # Start recording
    stream = audio.open(
        format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
    )

    print("Recording...")

    frames = []

    # Record data for 10 seconds
    for _ in range(0, int(RATE / CHUNK * record_seconds)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording.")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recorded data as a WAV file
    filename = WAVE_OUTPUT_FILENAME.format(len(os.listdir("audio_samples")))
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))
    print(f"Audio saved as {filename}")

    return filename

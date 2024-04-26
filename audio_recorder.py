import pyaudio
import wave
import os
from tkinter import Tk, Button

# Constants
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "audio_samples/sample_{}.wav"

# Create directory for audio_samples if it doesn't exist
if not os.path.exists("audio_samples"):
    os.makedirs("audio_samples")

def record_audio():
    audio = pyaudio.PyAudio()

    # Start recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("Recording...")

    frames = []

    # Record data for 10 seconds
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording.")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recorded data as a WAV file
    filename = WAVE_OUTPUT_FILENAME.format(len(os.listdir("audio_samples")))
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    print(f"Audio saved as {filename}")

# Set up the GUI
root = Tk()
root.title("Audio Recorder")
button = Button(root, text="Record", command=record_audio)
button.pack()

# Start the GUI event loop
root.mainloop()

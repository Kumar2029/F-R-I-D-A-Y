import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import time

def list_devices():
    print("Available Audio Devices:")
    print(sd.query_devices())
    print("\nDefault Input Device:")
    try:
        print(sd.query_devices(kind='input'))
    except Exception as e:
        print(f"Error querying default input: {e}")

def test_recording():
    fs = 44100
    duration = 5
    print(f"\nRecording for {duration} seconds... SPEAK NOW!")
    try:
        myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        print("Recording complete.")
        
        filename = "debug_output.wav"
        wav.write(filename, fs, myrecording)
        print(f"Saved to {filename}")
        
        print("Playing back recorded audio... Listen carefully.")
        sd.play(myrecording, fs)
        sd.wait()
        print("Playback complete.")
        
    except Exception as e:
        print(f"Recording/Playback failed: {e}")

if __name__ == "__main__":
    list_devices()
    test_recording()


import sounddevice as sd
import numpy as np
import time

def monitor_audio(duration=5):
    print(f"\nMonitoring audio for {duration} seconds (int16 mode)...")
    print("Please speak into the microphone...")
    
    def callback(indata, frames, time, status):
        # Match SpeechToText.py calculation exactly
        temp_data = indata.astype(np.float64)
        rms = np.sqrt(np.mean(temp_data**2))
        print(f"RMS: {rms:.2f}", end='\r')

    try:
        # Use dtype='int16' to match SpeechToText.py
        with sd.InputStream(callback=callback, dtype='int16', channels=1):
            sd.sleep(duration * 1000)
    except Exception as e:
        print(f"Error opening stream: {e}")

if __name__ == "__main__":
    try:
        monitor_audio()
    except Exception as e:
        print(f"An error occurred: {e}")

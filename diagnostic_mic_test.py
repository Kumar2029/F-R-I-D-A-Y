
import sounddevice as sd
import numpy as np
import time

def list_devices():
    print("Available Input Devices:")
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            print(f"{i}: {dev['name']}")
    return devices

def monitor_audio(duration=5):
    print(f"\nMonitoring audio for {duration} seconds...")
    print("Please speak into the microphone...")
    
    def callback(indata, frames, time, status):
        volume_norm = np.linalg.norm(indata) * 10
        print(f"Volume: {volume_norm:.2f}", end='\r')

    try:
        with sd.InputStream(callback=callback):
            sd.sleep(duration * 1000)
    except Exception as e:
        print(f"Error opening stream: {e}")

if __name__ == "__main__":
    try:
        list_devices()
        monitor_audio()
    except Exception as e:
        print(f"An error occurred: {e}")

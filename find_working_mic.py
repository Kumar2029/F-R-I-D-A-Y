import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import time

def find_mic():
    devices = sd.query_devices()
    print("Testing microphones...")
    
    input_devices = []
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            input_devices.append((i, dev['name']))

    if not input_devices:
        print("No input devices found!")
        return

    fs = 44100
    duration = 4
    
    for idx, name in input_devices:
        print(f"\n------------------------------------------------")
        print(f"Testing Device #{idx}: {name}")
        print(f"Recording per 4 seconds... SPEAK NOW into this device!")
        try:
            # Record
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16', device=idx)
            sd.wait()
            
            print("Playing back...")
            sd.play(recording, fs, device=None) # Play on default output
            sd.wait()
            print("Playback complete.")
            print(f"DID YOU HEAR YOURSELF? If yes, remember Device #{idx}.")
            time.sleep(1)
            
        except Exception as e:
            print(f"Failed to test device #{idx}: {e}")

if __name__ == "__main__":
    find_mic()

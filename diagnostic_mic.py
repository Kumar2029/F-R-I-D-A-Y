import sounddevice as sd
import numpy as np

def check_mics():
    devices = sd.query_devices()
    print("Available devices:")
    print(devices)
    
    input_devices = [i for i, d in enumerate(devices) if d['max_input_channels'] > 0]
    
    if not input_devices:
        print("No input devices found.")
        return

    print(f"\nScanning {len(input_devices)} input devices for signal...")
    
    for idx in input_devices:
        dev_name = devices[idx]['name']
        print(f"\nTesting Device {idx}: {dev_name}")
        try:
            # Record 1 second
            duration = 1.0
            fs = 44100
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32', device=idx)
            sd.wait()
            
            # Calculate RMS amplitude
            rms = np.sqrt(np.mean(recording**2))
            decibel = 20 * np.log10(rms) if rms > 0 else -np.inf
            
            print(f"  -> RMS: {rms:.6f} | dB: {decibel:.2f}")
            
            if rms > 0.01: # Arbitrary threshold for "sound detected"
                print("  -> STATUS: **SIGNAL DETECTED** (Likely working mic)")
            elif rms > 0.001:
                print("  -> STATUS: Weak signal (Background noise?)")
            else:
                print("  -> STATUS: Silent/Dead")
                
        except Exception as e:
            print(f"  -> Error: {e}")

if __name__ == "__main__":
    check_mics()

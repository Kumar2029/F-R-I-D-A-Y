from dotenv import dotenv_values
import speech_recognition as sr
import os
import mtranslate as mt
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import time
import queue

# Load environment variables
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en")
EnergyThreshold = int(env_vars.get("EnergyThreshold", 400)) # Amplitude threshold
RecordTimeout = float(env_vars.get("RecordTimeout", 5))
SeachTimeout = float(env_vars.get("SeachTimeout", 2)) # Silence time to stop recording

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    if not query_words:
        return new_query

    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation

def SetAssistantStatus(Status):
    current_dir = os.getcwd()
    TempDirPath = os.path.join(current_dir, "Frontend", "Files")
    os.makedirs(TempDirPath, exist_ok=True)
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding='utf-8') as file:
        file.write(Status)

def SpeechRecognition():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = EnergyThreshold
    recognizer.dynamic_energy_threshold = False 
    recognizer.pause_threshold = 0.8  # Short pause before considering phrase complete
    
    print("Initializing microphone...")
    SetAssistantStatus("Initializing...")
    
    # Queue to hold audio blocks
    q = queue.Queue()
    
    def callback(indata, frames, time, status):
        # This is called (from a separate thread) for each audio block.
        if status:
            print(status, flush=True)
        q.put(indata.copy())

    device_info = sd.query_devices(kind='input')
    samplerate = int(device_info['default_samplerate'])
    
    # We will record raw audio
    # State machine: 
    # 0 = Waiting for speech (RMS < Threshold)
    # 1 = Recording speech (RMS > Threshold)
    # 2 = Silence timeout (RMS < Threshold for X seconds) -> OFF
    
    status_print = False
    
    try:
        with sd.InputStream(samplerate=samplerate, channels=1, callback=callback, dtype='int16'):
            print("Listening... (Speak now)")
            SetAssistantStatus("Listening...")
            
            frames = []
            recording = False
            last_speech_time = 0
            start_speech_time = 0
            
            while True:
                data = q.get()
                
                # Calculate energy (RMS)
                # int16 range is -32768 to 32767. 
                # RMS can be large. 
                # We need to convert to float for calculation or handle overflow
                temp_data = data.astype(np.float64)
                rms = np.sqrt(np.mean(temp_data**2))
                
                current_time = time.time()
                
                if rms > EnergyThreshold:
                    if not recording:
                        print("Speech Detected! Recording...")
                        SetAssistantStatus("Listening (Speech Detected)...")
                        recording = True
                        start_speech_time = current_time
                        
                    last_speech_time = current_time
                    frames.append(data)
                
                elif recording:
                    # We are currently recording but instant energy is low.
                    # Check if we have timed out (silence for X seconds)
                    frames.append(data) # Keep recording silence briefly
                    
                    if current_time - last_speech_time > SeachTimeout:
                        print("Silence detected. Processing...")
                        break
                        
                    if current_time - start_speech_time > RecordTimeout:
                        print("Max recording time reached. Processing...")
                        break
                        
                else:
                    # Waiting for speech, just discard (or keep a small buffer if we wanted pre-roll)
                    pass
            
            # End of loop, we have `frames` with audio
            print("Finished recording.")
            SetAssistantStatus("Recognizing...")
            
            # Concatenate all blocks
            recording_data = np.concatenate(frames, axis=0)
            
            # Save to temp wav
            temp_wav = "temp_input.wav"
            wav.write(temp_wav, samplerate, recording_data)
            
            # Process with SpeechRecognition
            try:
                with sr.AudioFile(temp_wav) as source:
                    audio_data = recognizer.record(source)
                    # Use Google Speech Recognition
                    text = recognizer.recognize_google(audio_data, language="en-US" if "en" in InputLanguage else InputLanguage)
                    
                    print(f"User said: {text}")
                    SetAssistantStatus("Processing...")
                    
                    if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                        return QueryModifier(text)
                    else:
                        SetAssistantStatus("Translating...")
                        return QueryModifier(UniversalTranslator(text))

            except sr.UnknownValueError:
                print("Could not understand audio")
                return ""
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                return ""
            finally:
                if os.path.exists(temp_wav):
                    os.remove(temp_wav)

    except Exception as e:
        print(f"Error in speech recognition: {e}")
        return ""


def SpeechRecognitionConfirmation(timeout=5, energy_threshold_override=None):
    """
    Dedicated mode for capturing short Yes/No confirmations.
    Uses sounddevice (Raw) to bypass PyAudio dependency.
    """
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = energy_threshold_override if energy_threshold_override else EnergyThreshold
    recognizer.dynamic_energy_threshold = False 
    recognizer.pause_threshold = 0.6 
    
    print(f"Initializing confirmation listener (Timeout: {timeout}s)...")
    
    q = queue.Queue()
    
    def callback(indata, frames, time, status):
        # Callback for sounddevice
        if status:
            print(status, flush=True)
        q.put(indata.copy())

    try:
        device_info = sd.query_devices(kind='input')
        samplerate = int(device_info['default_samplerate'])
        
        with sd.InputStream(samplerate=samplerate, channels=1, callback=callback, dtype='int16'):
            print("Confirmation Listening... (Say YES or NO)")
            
            frames = []
            recording = False
            last_speech_time = 0
            start_speech_time = 0
            
            start_time = time.time()
            
            while True:
                # Global safety timeout
                if time.time() - start_time > timeout + 2.0: 
                    print("Confirmation Timeout (Hard Limit).")
                    break

                try:
                    data = q.get(timeout=0.5)
                except queue.Empty:
                    # Check overall timeout if queue is empty
                    if time.time() - start_time > timeout and not recording:
                         print("Confirmation Timeout (No speech).")
                         break
                    continue
                
                temp_data = data.astype(np.float64)
                rms = np.sqrt(np.mean(temp_data**2))
                current_time = time.time()
                
                if rms > recognizer.energy_threshold:
                    if not recording:
                        print("Confirmation Speech Detected!")
                        recording = True
                        start_speech_time = current_time
                    last_speech_time = current_time
                    frames.append(data)
                
                elif recording:
                    frames.append(data)
                    # Silence timeout (shorter for confirmation)
                    if current_time - last_speech_time > 0.8:  # 0.8s silence
                        print("Confirmation Silence detected. Stop.")
                        break
                    # Max duration for confirmation (short)
                    if current_time - start_speech_time > 3.0: 
                         print("Confirmation Max duration. Stop.")
                         break
                else:
                    # Waiting... Check timeout
                    if current_time - start_time > timeout:
                        print("Confirmation Timeout (Wait expired).")
                        break
            
            if not frames:
                return ""
                
            print("Processing Confirmation...")
            recording_data = np.concatenate(frames, axis=0)
            temp_wav = "temp_confirm.wav"
            wav.write(temp_wav, samplerate, recording_data)
            
            try:
                with sr.AudioFile(temp_wav) as source:
                    audio_data = recognizer.record(source)
                    text = recognizer.recognize_google(audio_data, language="en-US")
                    print(f"Confirmation Heard: {text}")
                    return text.lower().strip()
            except sr.UnknownValueError:
                print("Confirmation: Audio not understood.")
                return ""
            except Exception as e:
                print(f"Confirmation Error: {e}")
                return ""
            finally:
                if os.path.exists(temp_wav):
                    os.remove(temp_wav)
                    
    except Exception as e:
        print(f"Confirmation Microphone Error: {e}")
        return ""

if __name__ == "__main__":
    while True:
        Text = SpeechRecognition()
        if Text:
            print(f"Final Result: {Text}")

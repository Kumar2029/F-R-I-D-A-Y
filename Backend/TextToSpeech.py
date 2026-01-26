import asyncio
import tempfile
import os

import pygame
import edge_tts

# Optional offline fallback
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False


async def _edge_tts_async(text: str):
    communicate = edge_tts.Communicate(
        text=text,
        voice="en-US-AriaNeural"
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        audio_path = f.name

    await communicate.save(audio_path)

    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)

    try:
        os.remove(audio_path)
    except Exception:
        pass


def _fallback_pyttsx3(text: str):
    if not PYTTSX3_AVAILABLE:
        print("[TTS] pyttsx3 not available. Skipping fallback.")
        return

    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        print("[TTS] Used pyttsx3 fallback.")
    except Exception as e:
        print(f"[TTS] pyttsx3 fallback failed: {e}")


def TTS(text: str):
    if not text or not text.strip():
        return

    print(f"[TTS] CALLED with text: {text}")

    try:
        # If an event loop already exists, schedule task
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(_edge_tts_async(text))
        except RuntimeError:
            asyncio.run(_edge_tts_async(text))

    except Exception as e:
        print(f"[TTS] edge-tts failed: {e}")
        _fallback_pyttsx3(text)
from typing import List
try:
    from pycaw.pycaw import AudioUtilities
except ImportError:
    AudioUtilities = None

def get_active_audio_sessions() -> List[str]:
    """
    Returns a list of process names that have an active audio session.
    """
    if not AudioUtilities:
        return []
    
    active_apps = []
    try:
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process:
                active_apps.append(session.Process.name())
    except Exception as e:
        print(f"[AudioUtils] Error getting sessions: {e}")
        return []
    
    return active_apps

def is_audio_playing(process_name_substring: str) -> bool:
    """
    Checks if a process with the given substring is playing audio.
    Note: PyCaw checks session existence, not necessarily 'playing' state directly without deeper inspection.
    But usually, a session exists if the app has initialized audio.
    """
    sessions = get_active_audio_sessions()
    for s in sessions:
        if process_name_substring.lower() in s.lower():
            return True
    return False

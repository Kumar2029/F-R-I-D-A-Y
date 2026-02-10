import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Mock dependencies BEFORE import
sys.modules["Backend.Automation"] = MagicMock()
sys.modules["Backend.SpeechToText"] = MagicMock()
sys.modules["speech_recognition"] = MagicMock()
sys.modules["pycaw"] = MagicMock()
sys.modules["pycaw.pycaw"] = MagicMock()

# Adjust path to include project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Backend.MediaController import MediaController
from core.intents import MediaIntent

class TestMediaController(unittest.TestCase):
    def setUp(self):
        self.controller = MediaController()
        
    def test_normalize_intent_simple(self):
        intent = self.controller.normalize_intent("play Blinding Lights")
        self.assertEqual(intent.query, "blinding lights")
        self.assertIsNone(intent.platform_hint)
        self.assertEqual(intent.action, "play")

    def test_normalize_intent_spotify(self):
        intent = self.controller.normalize_intent("play Blinding Lights on Spotify")
        self.assertEqual(intent.query, "blinding lights")
        self.assertEqual(intent.platform_hint, "spotify")

    def test_normalize_intent_youtube(self):
        intent = self.controller.normalize_intent("play Blinding Lights on YouTube")
        self.assertEqual(intent.query, "blinding lights")
        self.assertEqual(intent.platform_hint, "youtube")

    def test_resolve_platform_explicit(self):
        intent = MediaIntent(action="play", query="test", platform_hint="spotify")
        platforms = self.controller.resolve_platform(intent)
        self.assertEqual(platforms[0], "spotify")
        self.assertIn("youtube", platforms)

    def test_resolve_platform_default(self):
        intent = MediaIntent(action="play", query="test")
        platforms = self.controller.resolve_platform(intent)
        self.assertEqual(platforms[0], "spotify") # Default preference

    @patch("automation.spotify.play")
    @patch("automation.youtube_playback.play")
    def test_execution_fallback(self, mock_youtube, mock_spotify):
        # Setup: Spotify fails, YouTube succeeds
        mock_spotify.return_value = False
        mock_youtube.return_value = True
        
        intent = MediaIntent(action="play", query="test", platform_hint="spotify")
        
        # Execute
        result = self.controller.execute(intent)
        
        # Verify
        mock_spotify.assert_called_once()
        mock_youtube.assert_called_once()
        self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()

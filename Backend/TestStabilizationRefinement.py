import unittest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from Backend.outcomes import Outcome
# Import Automation functions to test
from Backend.Automation import TranslateAndExecute, execute_step

class TestStabilizationRefinement(unittest.IsolatedAsyncioTestCase):
    async def test_speak_action(self):
        print("\nTesting 'speak' action...")
        with patch('Backend.Automation.TTS') as mock_tts:
            # Test direct execute_step
            outcome = await execute_step("speak", "Hello World")
            self.assertTrue(outcome.success)
            mock_tts.assert_called_with("Hello World")
            print("speak action executed TTS successfully.")

    async def test_whatsapp_none_message(self):
        print("\nTesting send_whatsapp 'None' rejection...")
        
        # We need to capture the generator output of TranslateAndExecute
        commands = ["send_whatsapp Mom | None"]
        
        # Mock secure_send_whatsapp so it doesn't actually run if logic fails
        with patch('Backend.Automation.secure_send_whatsapp', new_callable=AsyncMock) as mock_send:
            # Iterate async generator
            results = []
            async for res in TranslateAndExecute(commands):
                results.append(res)
            
            # Verify outcome failure
            self.assertFalse(results[0].success)
            self.assertIn("content missing", results[0].reason)
            
            # Verify secure_send_whatsapp was NOT called
            mock_send.assert_not_called()
            print("send_whatsapp rejected 'None' message successfully.")

    async def test_whatsapp_empty_message(self):
        print("\nTesting send_whatsapp empty message rejection...")
        commands = ["send_whatsapp Mom | "]
        
        with patch('Backend.Automation.secure_send_whatsapp', new_callable=AsyncMock) as mock_send:
            results = []
            async for res in TranslateAndExecute(commands):
                results.append(res)
            
            # Verify outcome failure
            self.assertFalse(results[0].success)
            mock_send.assert_not_called()
            print("send_whatsapp rejected empty message successfully.")

if __name__ == '__main__':
    unittest.main()

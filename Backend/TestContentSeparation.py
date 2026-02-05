import unittest
from unittest.mock import MagicMock, patch
from Backend.GoalExtractor import GoalExtractor
from Backend.contracts import Goal

class TestContentSeparation(unittest.TestCase):
    def setUp(self):
        self.extractor = GoalExtractor()

    def test_content_extraction(self):
        print("\nTesting Content Extraction...")
        inputs = [
            "write a python script",
            "explain quantum physics",
            "generate a story about cats",
            "code a bubble sort"
        ]
        for i in inputs:
            goal = self.extractor.extract_goal(i)
            print(f"Input: '{i}' -> {goal.response_mode}")
            self.assertEqual(goal.response_mode, "CONTENT")
            self.assertEqual(goal.name, "generate_content")

    def test_action_extraction(self):
        print("\nTesting Action Extraction...")
        inputs = [
            "send message to Mom saying Hi",
            "search for tacos",
            "open Chrome",
            "play Despacito"
        ]
        for i in inputs:
            goal = self.extractor.extract_goal(i)
            print(f"Input: '{i}' -> {goal.response_mode}")
            self.assertEqual(goal.response_mode, "ACTION")
            
    def test_query_extraction(self):
        print("\nTesting Query/Clarification Extraction...")
        # Missing params
        inputs = [
            "send message to Mom", # Missing content
            "send a message", # Ambiguous
            "tell Dad" # Missing content
        ]
        for i in inputs:
            goal = self.extractor.extract_goal(i)
            print(f"Input: '{i}' -> {goal.response_mode} ({goal.content})")
            self.assertEqual(goal.response_mode, "QUERY")
            self.assertEqual(goal.name, "clarify")

    def test_unsupported_is_query(self):
        print("\nTesting Unsupported -> Query...")
        goal = self.extractor.extract_goal("do a barrel roll")
        self.assertEqual(goal.response_mode, "QUERY")
        self.assertEqual(goal.name, "clarify")
        print("Unsupported input mapped to QUERY successfully.")

if __name__ == '__main__':
    unittest.main()

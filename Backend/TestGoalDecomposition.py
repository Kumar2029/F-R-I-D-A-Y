from Backend.GoalDecomposer import GoalDecomposer
from Backend.contracts import Goal
import unittest

class TestGoalDecomposer(unittest.TestCase):
    def setUp(self):
        self.decomposer = GoalDecomposer()

    def test_send_message_decomposition(self):
        goal = Goal(name="send_message", target="Mom", content="Hi there")
        subgoals = self.decomposer.decompose(goal)
        
        self.assertEqual(len(subgoals), 1)
        self.assertEqual(subgoals[0].description, "send message to Mom saying Hi there")
        print(f"[Pass] Send Message -> {subgoals[0].description}")

    def test_search_web_decomposition(self):
        goal = Goal(name="search_web", target="Python Programming")
        subgoals = self.decomposer.decompose(goal)
        
        self.assertEqual(len(subgoals), 1)
        self.assertEqual(subgoals[0].description, "search for Python Programming")
        print(f"[Pass] Search Web -> {subgoals[0].description}")

    def test_generate_image_decomposition(self):
        goal = Goal(name="generate_image", content="A futuristic city") # target might be None
        subgoals = self.decomposer.decompose(goal)
        
        self.assertEqual(len(subgoals), 1)
        self.assertEqual(subgoals[0].description, "generate image of A futuristic city")
        print(f"[Pass] Generate Image -> {subgoals[0].description}")

if __name__ == '__main__':
    unittest.main()

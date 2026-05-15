import unittest
from backend.memory import AgentMemory

class TestAgentMemory(unittest.TestCase):
    def test_add_finding(self):
        memory = AgentMemory(topic="Test Topic")
        memory.add_finding("Question 1", [{"summary": "Summary 1", "url": "http://example.com"}])
        self.assertEqual(len(memory.findings), 1)
        self.assertEqual(memory.findings[0]["question"], "Question 1")

    def test_to_context_string(self):
        memory = AgentMemory(topic="Test Topic")
        memory.add_finding("Question 1", [{"summary": "Summary 1", "url": "http://example.com"}])
        context = memory.to_context_string()
        self.assertIn("Research Topic: Test Topic", context)
        self.assertIn("Sub-question 1: Question 1", context)
        self.assertIn("- Summary 1 (source: http://example.com)", context)

if __name__ == "__main__":
    unittest.main()

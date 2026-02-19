import unittest

from app.intents.intent_detector import detect_intent


class TestDetectIntentInvalidInputs(unittest.TestCase):
    def test_none_input_returns_no_intent(self):
        self.assertEqual(detect_intent(None), (None, 0.0))

    def test_empty_string_returns_no_intent(self):
        self.assertEqual(detect_intent(""), (None, 0.0))

    def test_whitespace_only_string_returns_no_intent(self):
        self.assertEqual(detect_intent("   \t\n  "), (None, 0.0))

    def test_non_string_input_returns_no_intent(self):
        self.assertEqual(detect_intent(123), (None, 0.0))


if __name__ == "__main__":
    unittest.main()

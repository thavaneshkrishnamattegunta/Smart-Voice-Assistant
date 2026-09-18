import os
import unittest
from unittest import mock

import gemini_ai


class GeminiAIConfigTests(unittest.TestCase):
    def test_missing_api_key_returns_config_message(self):
        original_key = os.environ.get("GEMINI_API_KEY")
        os.environ.pop("GEMINI_API_KEY", None)
        try:
            with mock.patch.object(gemini_ai, "model", None):
                self.assertEqual(
                    gemini_ai.ask_gemini("hello"),
                    "Gemini API key is not configured. Set the GEMINI_API_KEY environment variable."
                )
        finally:
            if original_key is not None:
                os.environ["GEMINI_API_KEY"] = original_key


if __name__ == "__main__":
    unittest.main()

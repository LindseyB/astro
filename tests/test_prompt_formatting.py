import unittest
from pathlib import Path


class TestPromptFormatting(unittest.TestCase):
    def test_daily_horoscope_prompt_has_consistent_dos_and_donts_format(self):
        calculations_path = Path(__file__).resolve().parents[1] / "calculations.py"
        content = calculations_path.read_text(encoding="utf-8")

        self.assertIn("✅ Do:\\n\\n* item 1\\n* item 2\\n* item 3", content)
        self.assertIn("❌ Don't:\\n\\n* item 1\\n* item 2\\n* item 3", content)


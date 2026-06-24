import unittest
from pathlib import Path
from prompt_templates import load_prompt_template


class TestPromptFormatting(unittest.TestCase):
    def test_daily_horoscope_prompt_has_consistent_dos_and_donts_format(self):
        prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "calculations" / "chart_user.md"
        content = prompt_path.read_text(encoding="utf-8")
        prompt_template = load_prompt_template("calculations/chart_user.md")

        self.assertIn("✅ Do:\n\n* item 1\n* item 2\n* item 3", content)
        self.assertIn("❌ Don't:\n\n* item 1\n* item 2\n* item 3", content)
        self.assertEqual(prompt_template.metadata["role"], "user")
        self.assertEqual(prompt_template.metadata["temperature"], 1.0)
        self.assertIn("✅ Do:\n\n* item 1\n* item 2\n* item 3", prompt_template.content)

    def test_music_suggestion_prompt_metadata_is_available(self):
        prompt_template = load_prompt_template("routes/music_suggestion_user.md")

        self.assertEqual(prompt_template.metadata["role"], "user")
        self.assertEqual(prompt_template.metadata["temperature"], 0.4)
        self.assertIn("🎶 [Title] by [Artist]", prompt_template.content)

    def test_song_verification_prompt_metadata_is_available(self):
        prompt_template = load_prompt_template("ai_service/song_verification_user.md")

        self.assertEqual(prompt_template.metadata["role"], "user")
        self.assertEqual(prompt_template.metadata["temperature"], 0.3)
        self.assertEqual(prompt_template.metadata["max_tokens"], 500)


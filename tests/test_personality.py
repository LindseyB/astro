import unittest

from personality import (
    apply_personality_to_system_prompt,
    normalize_personality,
)


class TestPersonalityHelpers(unittest.TestCase):
    def test_normalize_personality_defaults_on_unknown(self):
        self.assertEqual(normalize_personality(None), 'default')
        self.assertEqual(normalize_personality('  DEFAULT  '), 'default')
        self.assertEqual(normalize_personality('unknown'), 'default')

    def test_apply_personality_to_system_prompt_appends_known_modes(self):
        base = 'You are an astrologer.'
        witchy = apply_personality_to_system_prompt(base, 'witchy')
        goth = apply_personality_to_system_prompt(base, 'goth')

        self.assertIn('crystals', witchy)
        self.assertIn('moon phases', witchy)
        self.assertIn('black emojis', goth)
        self.assertIn('ravens', goth)

    def test_apply_personality_to_system_prompt_keeps_default(self):
        base = 'You are an astrologer.'
        self.assertEqual(apply_personality_to_system_prompt(base, 'default'), base)

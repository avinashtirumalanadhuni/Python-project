"""
Automated unit tests for password generation, strength assessment, and clipboard integration.
"""

import unittest
from clipboard_helper import copy_to_clipboard, get_clipboard_text
from generator import (
    AMBIGUOUS_CHARS,
    DIGIT_CHARS,
    LOWERCASE_CHARS,
    SYMBOL_CHARS,
    UPPERCASE_CHARS,
    evaluate_strength,
    generate_password,
    get_available_pools,
)
from sound import generate_wav_buffer


class TestPasswordGenerator(unittest.TestCase):
    def test_length_enforcement(self):
        for length in [6, 12, 16, 32, 64]:
            pwd = generate_password(length=length)
            self.assertEqual(len(pwd), length)

    def test_character_pool_inclusion(self):
        # Generate password with all categories
        pwd = generate_password(
            length=32,
            use_upper=True,
            use_lower=True,
            use_digits=True,
            use_symbols=True,
            exclude_ambiguous=False,
        )
        has_upper = any(c in UPPERCASE_CHARS for c in pwd)
        has_lower = any(c in LOWERCASE_CHARS for c in pwd)
        has_digit = any(c in DIGIT_CHARS for c in pwd)
        has_symbol = any(c in SYMBOL_CHARS for c in pwd)

        self.assertTrue(has_upper, "Should contain uppercase letters")
        self.assertTrue(has_lower, "Should contain lowercase letters")
        self.assertTrue(has_digit, "Should contain digits")
        self.assertTrue(has_symbol, "Should contain symbols")

    def test_character_pool_exclusion(self):
        # Only digits
        pwd = generate_password(
            length=16,
            use_upper=False,
            use_lower=False,
            use_digits=True,
            use_symbols=False,
        )
        self.assertTrue(all(c in DIGIT_CHARS for c in pwd))

    def test_ambiguous_characters_exclusion(self):
        for _ in range(50):
            pwd = generate_password(
                length=30,
                use_upper=True,
                use_lower=True,
                use_digits=True,
                use_symbols=True,
                exclude_ambiguous=True,
            )
            for ch in pwd:
                self.assertNotIn(ch, AMBIGUOUS_CHARS)

    def test_strength_evaluation(self):
        # Empty
        score, label, _ = evaluate_strength("")
        self.assertEqual(score, 0)
        self.assertEqual(label, "None")

        # Weak password
        score_weak, label_weak, _ = evaluate_strength("12345")
        self.assertIn(label_weak, ["Very Weak", "Weak"])

        # Strong password
        score_strong, label_strong, _ = evaluate_strength("Tr0ub4dor&3#K99_!xQ")
        self.assertIn(label_strong, ["Strong", "Very Strong"])
        self.assertGreater(score_strong, score_weak)

    def test_clipboard_bridge(self):
        test_secret = "VaultPass-Secret-Test-12345!"
        copied = copy_to_clipboard(test_secret)
        self.assertTrue(copied, "Clipboard copy should succeed")
        read_back = get_clipboard_text()
        self.assertEqual(read_back, test_secret, "Clipboard content should match copied text")

    def test_procedural_audio_buffer(self):
        buf = generate_wav_buffer(0.05, lambda t, d: 440)
        self.assertIsNotNone(buf)
        data = buf.getvalue()
        # Ensure RIFF header exists
        self.assertTrue(data.startswith(b"RIFF"))


if __name__ == "__main__":
    unittest.main()

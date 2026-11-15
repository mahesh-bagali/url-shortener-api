import secrets
import string
import unittest
from unittest.mock import patch

from app.services.short_codes import ShortCodeGenerator


class ShortCodeGeneratorTests(unittest.TestCase):
    def test_generates_url_friendly_codes_of_configured_length(self) -> None:
        generator = ShortCodeGenerator(length=7)

        code = generator.generate()

        self.assertEqual(len(code), 7)
        self.assertTrue(set(code) <= set(string.ascii_letters + string.digits))

    def test_codes_are_unique_across_multiple_generations(self) -> None:
        generator = ShortCodeGenerator()

        codes = {generator.generate() for _ in range(100)}

        self.assertEqual(len(codes), 100)

    def test_retries_when_a_candidate_code_collides(self) -> None:
        generator = ShortCodeGenerator(length=6)
        first_candidate = iter("A" * 6)
        collision_then_new_code = iter("A" * 6 + "B" * 6)

        with patch(
            "app.services.short_codes.secrets.choice",
            side_effect=lambda _alphabet: next(first_candidate),
        ):
            first_code = generator.generate()

        with patch(
            "app.services.short_codes.secrets.choice",
            side_effect=lambda _alphabet: next(collision_then_new_code),
        ):
            second_code = generator.generate()

        self.assertEqual(first_code, "A" * 6)
        self.assertEqual(second_code, "B" * 6)

    def test_rejects_lengths_outside_supported_range(self) -> None:
        for length in (5, 9):
            with self.subTest(length=length):
                with self.assertRaises(ValueError):
                    ShortCodeGenerator(length=length)


if __name__ == "__main__":
    unittest.main()

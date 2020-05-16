from unittest import TestCase

from src.util import generate_random_base_64


class Test(TestCase):
    def test_generate_random_bytes(self):
        self.assertLessEqual(20, len(generate_random_base_64()))
        self.assertLessEqual(27, len(generate_random_base_64(27)))

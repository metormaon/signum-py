from unittest import TestCase

from src.util import generate_random_base_64, validate_hashcash_zeros


class Test(TestCase):
    def test_generate_random_bytes(self):
        self.assertLessEqual(20, len(generate_random_base_64()))
        self.assertLessEqual(27, len(generate_random_base_64(27)))

    def test_validate_hashcash_zeros(self):
        self.assertTrue(validate_hashcash_zeros(str.encode("15:20200516-184239:82.81.223.44:G5V-uz1mchswi07fqx0"
                                                           "QumL8LO0:MS4zMzczODkzNzkyNzY0MDM0ZSszMDc=:MjIwMQ=="), 15))

# -*- coding: utf-8 -*-

import os
from unittest import TestCase

from src.captcha import generate_captcha_challenge


class TestCaptcha(TestCase):
    def test_generate_captcha_challenge(self):
        test_resources_folder = os.path.dirname(os.path.realpath(__file__)) + "/test_resources"

        for _ in range(50):
            url, solution = generate_captcha_challenge(test_resources_folder + "/test_captcha_images")

            with open(test_resources_folder + f"/captcha{next(iter(solution))}.data", "rt") as f:
                actual_urls = f.read().splitlines()
                self.assertIn(url, actual_urls)

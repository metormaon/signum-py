import os
import sys
from unittest import TestCase

from src.captcha import generate_captcha_challenge


class TestCaptcha(TestCase):
    def test_generate_captcha_challenge(self):
        print(os.path.abspath(os.curdir))

            # generate_captcha_challenge("test/test_resources/test_captcha_images"))

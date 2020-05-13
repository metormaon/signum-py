# -*- coding: utf-8 -*-
import glob
import os
import random
import shutil
import tempfile
from unittest import TestCase

from src.captcha import generate_captcha_challenge, require_singular, allow_plural


class TestCaptcha(TestCase):
    test_resources_folder = os.path.dirname(os.path.realpath(__file__)) + "/test_resources"

    def test_generate_captcha_challenge(self):
        for _ in range(50):
            url, solution = generate_captcha_challenge(self.test_resources_folder + "/test_captcha_images")

            with open(self.test_resources_folder + f"/captcha{next(iter(solution))}.data", "rt") as f:
                actual_urls = f.read().splitlines()
                self.assertIn(url, actual_urls)

    def test_bad_path(self):
        with self.assertRaises(ValueError) as context:
            generate_captcha_challenge("bad/path")

        self.assertTrue('Bad or empty path: bad/path' in str(context.exception))

    def test_empty_path(self):
        temp = tempfile.mkdtemp()

        with self.assertRaises(ValueError) as context:
            generate_captcha_challenge(temp)

        self.assertTrue(f'Bad or empty path: {temp}' in str(context.exception))

    def test_single_subfoldered_path(self):
        temp = tempfile.mkdtemp()
        tempfile.mkdtemp(dir=temp)

        with self.assertRaises(ValueError) as context:
            generate_captcha_challenge(temp)

        self.assertTrue(f'Root folder has only one subdirectory: {temp}' in str(context.exception))

    def test_not_enough_images_in_folders(self):
        for _ in range(50):
            temp = tempfile.mkdtemp()

            shutil.copytree(self.test_resources_folder + "/test_captcha_images", temp + "/test_captcha_images")

            for folder_to_delete_from in random.sample(range(1,2+1),random.randint(1,2)):
                for suffix_to_delete in random.sample(range(1,3+1),random.randint(1,3)):
                    os.remove(f"{temp}/test_captcha_images/"
                              f"{folder_to_delete_from}/{folder_to_delete_from}-{suffix_to_delete}.png")

            with self.assertRaises(ValueError) as context:
                generate_captcha_challenge(temp + "/test_captcha_images")

            self.assertTrue('Not enough images in sub-directory ' in str(context.exception))

    def test_require_singular(self):
        self.assertEqual({"joe"}, require_singular("joe"))

    def test_allow_plural(self):
        self.assertEqual({"Joe", "Joes"}, allow_plural("Joe"))
        self.assertEqual({"baby", "babies"}, allow_plural("baby"))
        self.assertEqual({"baby", "babies"}, allow_plural("babies"))
        self.assertEqual({"piano", "pianos"}, allow_plural("piano"))
        self.assertEqual({"34", "34S"}, allow_plural("34"))

    def test_correct_solutions(self):
        image_folder = os.path.dirname(os.path.realpath(__file__)) + "/../captcha-images"

        for _ in range(20):
            _, solution = generate_captcha_challenge(image_folder, require_singular)
            self.assertIn(next(iter(solution)), {os.path.basename(f) for f in glob.glob(image_folder + "/*")})

import os
from unittest import TestCase
from unittest.mock import Mock

from src import StateEncryptor
from src.authentication_preparer import Preparer


class TestPreparer(TestCase):
    def test_prepare_authentication(self):
        encryptor = Mock(spec=StateEncryptor)
        encryptor.encrypt_state.return_value = b'Hello world'

        configuration = {
            "captcha_directory": os.path.dirname(os.path.realpath(__file__)) + "/test_resources/test_captcha_images",
            "csrf_token_length": 17,
            "hashcash_server_string_length": 13,
            "hashcash_zero_count": 14,
            "passphrase_minimum_length": 12,
            "client_hash_cycles": 102,
            "client_hash_length": 23,
            "password_minimum_length": 16,
            "SIGNUM_TEST_MODE": True

        }

        result = Preparer.prepare_authentication(encryptor, configuration)

        self.assertTrue(result["captcha"].startswith("data:img/jpeg;base64"))
        self.assertLessEqual(17, len(result["csrfToken"]))
        self.assertEqual(b'Hello world', result["state"])

        unencrypted_state = result["unencrypted_state"]

        self.assertEqual(2, len(unencrypted_state["captcha_solutions"]))

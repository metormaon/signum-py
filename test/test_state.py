import logging
import time
from unittest import TestCase

from src.state import StateEncryptor


class TestStateEncryptor(TestCase):
    def test_encryptor_on_bad_parameters(self):
        with self.assertRaises(ValueError) as e:
            StateEncryptor(state_aging_tolerance=-1)

        self.assertEqual("Bad state_aging_tolerance", str(e.exception))

        with self.assertRaises(ValueError) as e:
            StateEncryptor(state_aging_tolerance=0)

        self.assertEqual("Bad state_aging_tolerance", str(e.exception))

        with self.assertRaises(ValueError) as e:
            StateEncryptor(key_renewal_frequency=-1)

        self.assertEqual("Bad key_renewal_frequency", str(e.exception))

    def test_max_keys_calculation(self):
        # Default encryptor changes key every 30 sec and tolerates 120 sec, so it needs 5 keys
        self.assertEqual(5, StateEncryptor().max_keys)

        # Default key change frequency is 30 sec, so two keys are enough
        self.assertEqual(2, StateEncryptor(state_aging_tolerance=1).max_keys)

        # Default tolerance is 120 sec, so if we change key every 1 second, we need to remember 120+1 keys
        self.assertEqual(121, StateEncryptor(key_renewal_frequency=1).max_keys)

        # If keys are not renewed, one key is enough
        self.assertEqual(1, StateEncryptor(key_renewal_frequency=0).max_keys)

        # If renewal and tolerance are equal, 2 keys are enough
        self.assertEqual(2, StateEncryptor(state_aging_tolerance=20, key_renewal_frequency=20).max_keys)

        # If renewal is longer than tolerance, then 2 keys are enough
        self.assertEqual(2, StateEncryptor(state_aging_tolerance=10, key_renewal_frequency=20).max_keys)

        # If tolerance is longer than renewal, then we need enough keys to cover tolerance
        self.assertEqual(21, StateEncryptor(state_aging_tolerance=200, key_renewal_frequency=10).max_keys)

        with self.assertRaises(ValueError) as e:
            StateEncryptor(state_aging_tolerance=500, key_renewal_frequency=1)

        self.assertEqual("Keeping 501 keys is ridiculous.", str(e.exception))

    def test_simple_encryption_decryption(self):
        state_encryptor = StateEncryptor()

        state = {"hello": 2, "world": True}
        encryption = state_encryptor.encrypt_state(state)

        self.assertEqual(state, state_encryptor.decrypt_state(encryption))

    def test_aging_tolerance_failing(self):
        state_encryptor = StateEncryptor(state_aging_tolerance=1)

        state = {"hello": 2, "world": True}
        encryption = state_encryptor.encrypt_state(state)

        time.sleep(2)

        with self.assertRaises(ValueError) as e:
            state_encryptor.decrypt_state(encryption)

        self.assertEqual("Cannot decrypt state", str(e.exception))

    """Running the encryption mechanism end to end. The scheduler will run and schedule key renewals."""
    def test_renewing_keys(self):
        logging.basicConfig(level=logging.DEBUG)

        state_encryptor = StateEncryptor(state_aging_tolerance=6, key_renewal_frequency=1)

        try:
            state_encryptor.start()

            state = {"hello": 2, "world": True}
            encryption1 = state_encryptor.encrypt_state(state)

            time.sleep(2)

            encryption2 = state_encryptor.encrypt_state(state)

            time.sleep(2)

            self.assertEqual(state, state_encryptor.decrypt_state(encryption1))
            self.assertEqual(state, state_encryptor.decrypt_state(encryption2))

            self.assertTrue(4 <= len(state_encryptor._StateEncryptor__keys) <= 5)

        finally:
            state_encryptor.stop()

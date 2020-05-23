import logging
import pickle
import threading
import time
from typing import List

import schedule as schedule
from cryptography.fernet import Fernet, MultiFernet, InvalidToken

SCHEDULER_SLEEP_TIME = 1
REASONABLE_NUMBER_OF_KEYS = 500


class StateEncryptor(object):
    def __init__(self, state_aging_tolerance: int = 120, key_renewal_frequency: int = 30):
        if state_aging_tolerance <= 0:
            raise ValueError("Bad state_aging_tolerance")

        if key_renewal_frequency < 0:
            raise ValueError("Bad key_renewal_frequency")

        self.__state_aging_tolerance: int = state_aging_tolerance
        self.__key_renewal_frequency: int = key_renewal_frequency

        self.__max_keys = 1
        if key_renewal_frequency > 0:
            if state_aging_tolerance < key_renewal_frequency:
                self.__max_keys += 1
            else:
                self.__max_keys += state_aging_tolerance // key_renewal_frequency

        if self.__max_keys >= REASONABLE_NUMBER_OF_KEYS:
            raise ValueError(f"Keeping {self.__max_keys} keys is ridiculous.")

        self.__keys: List[Fernet] = []
        self.__renew_key()

        self.__encryptor: MultiFernet = MultiFernet(self.__keys)

        self.__thread_stop_event = threading.Event()

    def __renew_key(self):
        self.__keys.insert(0, Fernet(Fernet.generate_key()))
        self.__keys = self.__keys[:self.__max_keys]
        logging.debug(self.__keys)
        self.__encryptor = MultiFernet(self.__keys)

    def start(self):
        schedule.every(self.__key_renewal_frequency).seconds.do(self.__renew_key)
        thread = threading.Thread(target=self.__run_scheduler)
        thread.start()

    def stop(self):
        self.__thread_stop_event.set()

    def __run_scheduler(self):
        while not self.__thread_stop_event.is_set():
            schedule.run_pending()
            time.sleep(SCHEDULER_SLEEP_TIME)

    @property
    def max_keys(self):
        return self.__max_keys

    def encrypt_state(self, state: object) -> bytes:
        state_serialization = pickle.dumps(state)
        fernet_token = self.__encryptor.encrypt(state_serialization)
        return fernet_token

    def decrypt_state(self, encrypted_state: bytes) -> object:
        try:
            decrypted_state = self.__encryptor.decrypt(encrypted_state, self.__state_aging_tolerance)
            state = pickle.loads(decrypted_state)
        except InvalidToken as e:
            raise ValueError("Cannot decrypt state")

        return state





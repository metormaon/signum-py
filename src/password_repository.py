import abc
import hashlib
from typing import Tuple

MINIMAL_LENGTH_OF_SECURITY_STRING = 3


class PasswordRepository(abc.ABC):
    def __init__(self, username_hash_salt: str):
        PasswordRepository.verify_security_string_length(username_hash_salt, MINIMAL_LENGTH_OF_SECURITY_STRING,
                                                         "Username salt")
        self.username_hash_salt = username_hash_salt

    @abc.abstractmethod
    def _save_password(self, username: str, password: str) -> None:
        pass

    @abc.abstractmethod
    def _load_password(self, username: str) -> str:
        pass

    def save_password(self, username: str, password: str) -> None:
        PasswordRepository.verify_security_string_length(username, MINIMAL_LENGTH_OF_SECURITY_STRING,
                                                         "Username")

        PasswordRepository.verify_security_string_length(password, MINIMAL_LENGTH_OF_SECURITY_STRING,
                                                         "Password")

        hashed_username = PasswordRepository._hash_with_salt(hashable=username, salt=self.username_hash_salt)

        hashed_password = PasswordRepository._hash_with_salt(hashable=password, salt=hashed_username)

        self._save_password(hashed_username, hashed_password)

    def validate_password(self, username: str, password: str) -> Tuple[bool, str]:
        hashed_username = PasswordRepository._hash_with_salt(hashable=username, salt=self.username_hash_salt)

        hashed_password = self._load_password(hashed_username)

        if hashed_password:
            if hashed_password == self._hash_with_salt(password, hashed_username):
                return True, "Match"
            else:
                return False, "No match"
        else:
            return False, "Not found"

    @staticmethod
    def _hash_with_salt(hashable: str, salt: str) -> str:
        return hashlib.sha256(salt.encode() + hashable.encode()).hexdigest()

    @classmethod
    def verify_security_string_length(cls, string, minimal_length, field_name):
        if not string or len(string)<minimal_length:
            raise ValueError(f"{field_name} must be of at least {minimal_length} characters")


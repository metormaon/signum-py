from typing import Dict
from unittest import TestCase

from src.password_repository import PasswordRepository


class InMemoryPasswordRepository(PasswordRepository):
    def __init__(self, initial_setup: Dict[str, str] = None, username_hash_salt: str = "username_salt"):
        super().__init__(username_hash_salt)
        self.database: Dict[str, str] = initial_setup or {}

    def _save_password(self, username: str, password: str):
        self.database[username] = password

    def _load_password(self, username: str) -> str:
        return self.database.get(username)


class TestPasswordRepository(TestCase):
    def test_enforcement_of_secured_config(self):
        with self.assertRaises(ValueError) as e:
            # noinspection PyTypeChecker
            InMemoryPasswordRepository({}, None)
        self.assertEqual("Username salt must be of at least 3 characters", str(e.exception))

        with self.assertRaises(ValueError) as e:
            InMemoryPasswordRepository({}, "")
        self.assertEqual("Username salt must be of at least 3 characters", str(e.exception))

        with self.assertRaises(ValueError) as e:
            InMemoryPasswordRepository({}, " ")
        self.assertEqual("Username salt must be of at least 3 characters", str(e.exception))

        with self.assertRaises(ValueError) as e:
            # noinspection PyTypeChecker
            InMemoryPasswordRepository().save_password(None, "password")
        self.assertEqual("Username must be of at least 3 characters", str(e.exception))

        with self.assertRaises(ValueError) as e:
            InMemoryPasswordRepository().save_password("", "password")
        self.assertEqual("Username must be of at least 3 characters", str(e.exception))

        with self.assertRaises(ValueError) as e:
            InMemoryPasswordRepository().save_password(" ", "password")
        self.assertEqual("Username must be of at least 3 characters", str(e.exception))

        with self.assertRaises(ValueError) as e:
            # noinspection PyTypeChecker
            InMemoryPasswordRepository().save_password("username", None)
        self.assertEqual("Password must be of at least 3 characters", str(e.exception))

        with self.assertRaises(ValueError) as e:
            # noinspection PyTypeChecker
            InMemoryPasswordRepository().save_password("username", "")
        self.assertEqual("Password must be of at least 3 characters", str(e.exception))

        with self.assertRaises(ValueError) as e:
            # noinspection PyTypeChecker
            InMemoryPasswordRepository().save_password("username", " ")
        self.assertEqual("Password must be of at least 3 characters", str(e.exception))

    def test_validations(self):
        database = {
            "6226b64239e3b4131985f643f51123e123c8acc1cc692af8d296272b3edb0519":  # Joe
                "104d46c2c55d53459a01056b25597247ed2f572ff16f63dcbdb508ebbb7164ae"  # password
        }

        repository = InMemoryPasswordRepository(database)

        self.assertEqual((False, "Not found"), repository.validate_password("Moses", "password"))

        self.assertEqual((False, "No match"), repository.validate_password("Joe", "joe"))

        self.assertEqual((True, "Match"), repository.validate_password("Joe", "password"))

    def test_normal_flow(self):
        repository = InMemoryPasswordRepository()

        self.assertEqual((False, "Not found"), repository.validate_password("Joe", "password"))

        repository.save_password("Joe", "joe12#$m")

        self.assertEqual((False, "No match"), repository.validate_password("Joe", "password"))

        self.assertEqual((True, "Match"), repository.validate_password("Joe", "joe12#$m"))

    def test_salting_by_username(self):
        repository1 = InMemoryPasswordRepository({}, "username_salt_1")

        repository1.save_password("Joe", "joe12#$m")

        self.assertEqual((True, "Match"), repository1.validate_password("Joe", "joe12#$m"))

        repository2 = InMemoryPasswordRepository(repository1.database, "username_hash_2")

        self.assertEqual((False, "Not found"), repository2.validate_password("Joe", "joe12#$m"))

        repository2.save_password("Joe", "joe12#$m")

        self.assertEqual((True, "Match"), repository2.validate_password("Joe", "joe12#$m"))

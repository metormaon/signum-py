from datetime import datetime
from typing import Dict, Union, List, Set, Any

from . import StateEncryptor, captcha, util


class Preparer:
    @staticmethod
    def prepare_authentication(state_encryptor: StateEncryptor, configuration: Dict[str, Any]) -> Dict[str, Any]:
        captcha_url: str
        captcha_solution: Set[str]

        captcha_url, captcha_solutions = captcha.generate_captcha_challenge(configuration["captcha_directory"])

        csrf_token = util.generate_random_base_64(configuration["csrf_token_length"])
        hashcash_server_string = util.generate_random_base_64(configuration["hashcash_server_string_length"])

        state = {
            "server_time": datetime.utcnow().strftime("%Y%m%d-%H%M%S"),
            "captcha_solutions": captcha_solutions,
            "csrf_token": csrf_token,
            "hashcash": {
                "server_string": hashcash_server_string,
                "zero_count": configuration["hashcash_zero_count"]
            }
        }

        transaction_details: Dict[str, Any] = {
            "captcha": captcha_url,
            "server-instructions": f"""{{
                "captcha": {{
                    "require": true
                }},
                "hashcash": {{
                    "require": true,
                    "zeroCount": {int(configuration["hashcash_zero_count"])},
                    "serverString": "{hashcash_server_string}"
                }},
                "csrfToken": {{
                    "require": true
                }},
                "tolerance": {{
                    "minimumAlphabetPassphrase": {int(configuration["passphrase_minimum_length"])}
                }},
                "hashing": {{
                    saltHashByUsername: true,
                    hashCycles: {int(configuration["client_hash_cycles"])},
                    resultLength: {int(configuration["client_hash_length"])}
                }}
            }}""",
            "state": state_encryptor.encrypt_state(state),
            "csrfToken": csrf_token,
            "passtextStrength": f"""{{
                "minimumCharactersPassword": {int(configuration["password_minimum_length"])}
            }}""",
            "tolerance": f"""{{
                "minimumAlphabetPassphrase": {int(configuration["passphrase_minimum_length"])}
            }}"""
        }

        if configuration["SIGNUM_TEST_MODE"]:
            transaction_details["unencrypted_state"] = state

        return transaction_details

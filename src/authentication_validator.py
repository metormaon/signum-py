import datetime
import json
from json import JSONDecodeError
from typing import Tuple, Dict, List, Union

from src import util
from src.password_repository import PasswordRepository
from src.state import StateEncryptor


class AuthenticationValidator:
    @classmethod
    def validate(cls, request_details: Dict[str, str], headers: Dict[str, str], state_encryptor: StateEncryptor,
                 password_database: PasswordRepository, configuration: Dict[str, Union[str, List[str]]]) -> \
            Tuple[bool, object]:
        try:
            # ### Early tests - fast failure ### #

            # No referrer? A legitimate browser would have sent it. Fail.
            if not request_details.get("referrer"):
                return cls.failure("referrer", "not provided")

            # To validate the referrer, we need the host
            if not request_details.get("host"):
                return cls.failure("host", "not provided")

            # For the sake of the project, we support only http hosts
            acceptable_referrer = 'http://%s/' % request_details["host"]

            # The referrer should be a page on the same host
            if not request_details["referrer"].startswith(acceptable_referrer):
                return cls.failure("referrer", "doesn't match")

            remote_address = request_details.get("remote_addr")

            # Fail on missing remote address
            if not remote_address:
                return cls.failure("remote_address", "not provided")

            body = request_details.get("body")

            # Fail on missing body
            if not body:
                return cls.failure("body", "not provided")

            username = headers.get("X-Username")

            # Fail on missing username
            if not username:
                return cls.failure("username", "not provided")

            password = headers.get("X-hashed-Passtext")

            # Fail on missing username
            if not password:
                return cls.failure("password", "not provided")

            csrf = headers.get("X-Csrf-Token")

            # Fail on missing csrf token
            if not csrf:
                return cls.failure("csrf", "not provided")

            captcha = headers.get("X-Captcha")

            # Fail on missing captcha answer
            if not captcha:
                return cls.failure("captcha", "not provided")

            hashcash = headers.get("X-Hashcash")

            # Fail on missing hashcash
            if not hashcash:
                return cls.failure("hashcash", "not provided")

            # ### Hashcash validation ### #
            # Split hashcash into elements (the last two parts were calculated by the client to
            # achieve the zeros goal, so we ignore them
            try:
                zeros, timestamp, ip, server_string, _, _ = hashcash.split(":")
            except ValueError:
                return cls.failure("hashcash", "illegal structure")

            now = datetime.datetime.utcnow()
            # Convert timestamp to datetime object
            timestamp_object = datetime.datetime.strptime(timestamp, "%Y%m%d-%H%M%S")

            # Measure the age in seconds
            diff_in_seconds = (now - timestamp_object).total_seconds()

            submit_timeout = configuration.get("submit_timeout")
            assert submit_timeout, "Missing configuration item: submit_timeout"

            # Fail if timeout has been reached since the user has generated the hashcash
            if not 0 < diff_in_seconds <= float(submit_timeout):
                return cls.failure("hashcash", "hashcash timestamp exceeds timeout")

            self_ip_addresses = configuration.get("self_ip_addresses")
            assert self_ip_addresses is not None, "Missing configuration item: self_ip_addresses"

            if remote_address not in [ip] + self_ip_addresses:
                return cls.failure("hashcash", "ip address doesn't match: "+remote_address)

            if not cls.validate_hashcash(bytes(hashcash, "utf-8"), int(zeros)):
                return cls.failure("hashcash", "zeros not validated")

            try:
                data = json.loads(body)
                encrypted_state = data["state"]
                state = state_encryptor.decrypt_state(encrypted_state.encode())
            except JSONDecodeError:
                return cls.failure("body", "bad format")
            except (KeyError, AttributeError):
                return cls.failure("state", "not provided")
            except ValueError as e:
                return cls.failure("state", str(e))

            # Get server timestamp from state
            server_time = datetime.datetime.strptime(state["server_time"], "%Y%m%d-%H%M%S")

            # Measure login form age in seconds
            diff_in_seconds = (now - server_time).total_seconds()

            login_form_timeout = configuration.get("login_form_timeout")
            assert login_form_timeout, "Missing configuration item: login_form_timeout"

            # Fail if timeout has been reached since login form was generated
            if not 0 < diff_in_seconds <= float(login_form_timeout):
                return cls.failure("state", "login form age exceeds timeout")

            # Verify number of zeros in hashcash matches state
            if int(zeros) != int(state["hashcash"]["zero_count"]):
                return cls.failure("hashcash", "zeros don't match state")

            # Verify server string in hashcash matches state
            if server_string != state["hashcash"]["server_string"]:
                return cls.failure("hashcash", "server string doesn't match state")

            # Verify csrf token in hashcash matches state
            if csrf != state["csrf_token"]:
                return cls.failure("csrf", "csrf token doesn't match state")

            captcha_solutions = set(state["captcha_solutions"])

            # Verify captcha
            if captcha not in captcha_solutions:
                return cls.failure("captcha", f"captcha solution isn't in {captcha_solutions}")

            # Verify username-password
            passed, reason = password_database.validate_password(username=username, password=password)

            if not passed:
                return cls.failure("username-password", reason)

            # PASSED!!!!
            return True, {
                "visible_response": {
                    "passed": True,
                    "session_key": util.generate_random_base_64(40)
                }
            }

        except Exception as e:
            print(repr(e))
            return cls.failure("general", str(e))

    @staticmethod
    def validate_hashcash(hashcash: bytes, zero_count: int):
        return util.validate_hashcash_zeros(hashcash, zero_count)

    @staticmethod
    def failure(failure_stage: str, failure_reason: str):
        return False, {
            "visible_response": {
                "passed": False,
            },
            "security_details": {
                "failure_stage": failure_stage,
                "failure_reason": failure_reason
            }
        }

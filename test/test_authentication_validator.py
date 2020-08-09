from unittest import TestCase
from unittest.mock import Mock

from src.authentication_validator import AuthenticationValidator
from src.state import StateEncryptor


class TestAuthenticationValidator(TestCase):
    class TestValidator(AuthenticationValidator):
        @staticmethod
        def validate_hashcash(hashcash: bytes, zero_count: int):
            return True

    def setUp(self):
        self.request_details = {}
        self.headers = {}
        self.state_encryptor = Mock(spec=StateEncryptor)
        self.configuration = {}
        self.validator = AuthenticationValidator

    def validate(self):
        return self.validator.validate(request_details=self.request_details, headers=self.headers,
                                       state_encryptor=self.state_encryptor,
                                       configuration=self.configuration)

    def expect_failure(self, stage, reason):
        success, response = self.validate()

        self.assertFalse(success)
        self.assertFalse(response['visible_response']['passed'])

        self.assertEqual(stage, response['security_details']['failure_stage'])
        self.assertEqual(reason, response['security_details']['failure_reason'])

    def test_validation(self):
        self.expect_failure("referrer", "not provided")
        self.request_details["referrer"] = "http://www.host1.com/aloha"

        self.expect_failure("host", "not provided")
        self.request_details["host"] = "www.google.com"

        self.expect_failure("referrer", "doesn't match")
        self.request_details["host"] = "www.host1.com"

        self.expect_failure("requested_with", "not provided")
        self.headers["X-Requested-With"] = "the browser"

        self.expect_failure("requested_with", "not XmlHttpRequest")
        self.headers["X-Requested-With"] = "XmlHttpRequest"

        self.expect_failure("remote_address", "not provided")
        self.request_details["remote_addr"] = "135.136.137.138"

        self.expect_failure("body", "not provided")
        self.request_details["body"] = "state"

        self.expect_failure("csrf", "not provided")
        self.headers["X-Csrf-Token"] = "csrf_token"

        self.expect_failure("captcha", "not provided")
        self.headers["X-Captcha"] = "gremlins"

        self.expect_failure("hashcash", "not provided")
        self.headers["X-Hashcash"] = "mama"

        self.expect_failure("hashcash", "illegal structure")
        self.headers["X-Hashcash"] = "zeros:timestamp:ip:server_string:_:_"

        self.expect_failure("general", "time data 'timestamp' does not match format '%Y%m%d-%H%M%S'")
        self.headers["X-Hashcash"] = "zeros:20200730-153516:ip:server_string:_:_"
        self.configuration["submit_timeout"] = "0"

        self.expect_failure("hashcash", "hashcash timestamp exceeds timeout")
        self.configuration["submit_timeout"] = "100000000000000"

        self.configuration["self_ip_addresses"] = []
        self.expect_failure("hashcash", "ip address doesn't match: 135.136.137.138")
        self.headers["X-Hashcash"] = "zeros:20200730-153516:135.136.137.138:server_string:_:_"

        # The next issue (i.e. - passed so far)
        self.expect_failure("general", "invalid literal for int() with base 10: 'zeros'")

        self.headers["X-Hashcash"] = "zeros:20200730-153516:135.136.137.138:server_string:_:_"
        self.configuration["self_ip_addresses"] = ["127.0.0.1"]
        self.request_details["remote_addr"] = "127.0.0.1"

        # The next issue (i.e. - passed so far)
        self.expect_failure("general", "invalid literal for int() with base 10: 'zeros'")
        self.headers["X-Hashcash"] = "20:20200730-153516:135.136.137.138:server_string:_:_"

        self.expect_failure("hashcash", "zeros not validated")

        # Shushing the hashcash validator
        self.validator = TestAuthenticationValidator.TestValidator

        self.expect_failure("body", "bad format")
        self.request_details["body"] = "{}"

        self.expect_failure("state", "not provided")
        self.request_details["body"] = '{"state": {}}'

        self.expect_failure("state", "not provided")
        self.request_details["body"] = '{"state": "sdf"}'
        self.state_encryptor.decrypt_state = Mock(side_effect=ValueError("Cannot decrypt state"))

        self.expect_failure("state", "Cannot decrypt state")

        state = {
            "server_time": "20200730-153527",
            "captcha_solutions": ["zooka"],
            "csrf_token": "the_csrf_token",
            "hashcash": {
                "server_string": "the_server_string",
                "zero_count": 100
            }
        }

        self.state_encryptor.decrypt_state = Mock()
        self.state_encryptor.decrypt_state.return_value = state

        self.configuration["login_form_timeout"] = "0"

        self.expect_failure("state", "login form age exceeds timeout")
        self.configuration["login_form_timeout"] = "100000000000000"

        self.expect_failure("hashcash", "zeros don't match state")
        state["hashcash"]["zero_count"] = 20

        self.expect_failure("hashcash", "server string doesn't match state")
        state["hashcash"]["server_string"] = "server_string"

        self.expect_failure("csrf", "csrf token doesn't match state")
        state["csrf_token"] = "csrf_token"

        self.expect_failure("captcha", "captcha solution isn't in {'zooka'}")
        state["captcha_solutions"] = ["gremlin", "gremlins"]

        passed, response = self.validate()

        self.assertTrue(passed)
        self.assertTrue(response["visible_response"]["passed"])

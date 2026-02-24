import time

import pytest

from conftest import post_request
from fixtures.auth.fixture_reset_password import (
    FORGOT_PASS,
    OK,
    RESET_PASSWORD,
    SET_PASSWORD,
    SIGNUP,
    reset_password_params,
)
from utils.fake_data_generators import generate_email


@pytest.mark.reset_password
def test_post_api_auth_reset_password(post_request, reset_password_params):
    """
    Test the reset password API endpoint with various input combinations.

    This test verifies the behavior of the reset password endpoint by performing a signup request
    to obtain a valid token, setting a password, and then attempting to reset the password using
    the provided parameters.

    Args:
        post_request (callable): Fixture providing a function to make HTTP POST requests.
        reset_password_params (tuple): Fixture providing parameterized test data
                                     (password, nickname, timezone, expected_status).

    The test performs the following steps:
        - Sends a POST request to the signup endpoint to obtain a valid token using a generated email
          and 'en' as the language.
        - Sends a POST request to the set password endpoint to set an initial password using the
          obtained token, along with the provided password, nickname, and timezone from `reset_password_params`.
        - Sends a POST request to the reset password endpoint with the same token, password, and timezone.
        - Asserts that the response status code from the reset password request matches the expected status code.

    Assertions:
        - The response status code from the reset password endpoint must match the expected status code
          from `reset_password_params`.

    Fails if:
        - The status code does not match the expected value, including the response text in the error message.

    Note:
        - Assumes the `generate_email` function from `utils.fake_data_generators` provides a valid email.
        - The signup request is made with a fixed language ('en') to ensure a valid token is obtained.
        - The test assumes the set password request is necessary before resetting the password.
    """

    # post.signup
    signup_reponse = post_request(
        dict(zip(["email", "lang"], reset_password_params["signup"])), SIGNUP
    )

    # post.set_password
    post_request(
        dict(
            zip(
                ["token", "newPassword", "nickname", "timezone"],
                reset_password_params["set_pass"],
            ),
            token=signup_reponse.json()["token"],
        ),
        SET_PASSWORD,
    )

    # post.forgot_password
    forgot_pass_response = post_request(
        dict(
            reset_password_params["forgot_pass"], email=signup_reponse.json()["email"]
        ),
        FORGOT_PASS,
    )

    # post.reset_password
    reset_password_json = post_request(
        dict(reset_password_params["reset_pass"], token=forgot_pass_response.text),
        RESET_PASSWORD,
    )

    assert (
        reset_password_json.status_code == OK
    ), f"Expected status code {OK}, but got {reset_password_json.status_code}: {reset_password_json.text}"

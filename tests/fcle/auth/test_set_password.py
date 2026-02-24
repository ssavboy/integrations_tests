import pytest

from conftest import post_request
from fixtures.auth.fixture_set_password import SET_PASSWORD, SIGNUP, set_password_params
from utils.fake_data_generators import generate_email


@pytest.mark.set_password
def test_post_api_auth_set_password(post_request, set_password_params):
    """
    Test the set password API endpoint with various input combinations.

    This test verifies the behavior of the set password endpoint by first performing a signup request
    to obtain a valid token, then using that token to set a password with provided parameters.

    Args:
        post_request (callable): Fixture providing a function to make HTTP POST requests.
        set_password_params (tuple): Fixture providing parameterized test data
                                   (password, nickname, timezone, expected_status).

    The test performs the following steps:
        - Sends a POST request to the signup endpoint to obtain a valid token using a generated email
          and 'en' as the language.
        - Sends a POST request to the set password endpoint with the obtained token, along with the
          provided password, nickname, and timezone from `set_password_params`.
        - Asserts that the response status code matches the expected status code.

    Assertions:
        - The response status code from the set password endpoint must match the expected status code
          from `set_password_params`.

    Fails if:
        - The status code does not match the expected value, including the response text in the error message.

    Note:
        - Assumes the `generate_email` function from `utils.fake_data_generators` provides a valid email.
        - The signup request is made with a fixed language ('en') to ensure a valid token is obtained.
    """

    password, nickname, timezone, expected_status = set_password_params

    signup_reponse = post_request({"email": generate_email(), "lang": "en"}, SIGNUP)

    response = post_request(
        {
            "token": signup_reponse.json()["token"],
            "newPassword": password,
            "nickname": nickname,
            "timezone": timezone,
        },
        SET_PASSWORD,
    )

    assert (
        response.status_code == expected_status
    ), f"Expected status code {expected_status}, but got {response.status_code}: {response.text}"

import pytest

from conftest import post_request
from fixtures.auth.fixture_forgot_password import (
    FORGOT_PASSWORD,
    OK,
    SET_PASSWORD,
    SIGNUP,
    forgot_password_data,
)


@pytest.mark.forgot_password
def test_post_api_auth_forgot_password(post_request, forgot_password_data):
    """
    Test the forgot password API endpoint.

    This test verifies the behavior of the forgot password endpoint by performing a signup request
    to create a user, setting a password for that user, and then initiating a forgot password request
    using the provided test data.

    Args:
        post_request (callable): Fixture providing a function to make HTTP POST requests.
        forgot_password_data (dict): Fixture providing test data for signup, set password, and
                                   forgot password endpoints, including payloads for each.

    The test performs the following steps:
        - Sends a POST request to the signup endpoint with the signup payload from `forgot_password_data`.
        - Extracts the email from the signup response.
        - Sends a POST request to the set password endpoint using the set password payload from
          `forgot_password_data`, including the token from the signup response.
        - Updates the forgot password payload with the email from the signup response.
        - Sends a POST request to the forgot password endpoint with the updated payload.
        - Asserts that the response status code is 200 (OK).

    Assertions:
        - The response status code from the forgot password endpoint must be 200 (OK).

    Fails if:
        - The response status code is not 200, including the response text in the error message.

    Note:
        - Assumes the `forgot_password_data` fixture provides valid payloads for signup, set password,
          and forgot password endpoints.
        - The forgot password payload's email is updated with the email from the signup response to
          ensure consistency.
        - The test assumes the set password step is required before a forgot password request can be made.
    """

    signup_response = post_request(forgot_password_data["signup"], SIGNUP)

    post_request(
        dict(
            forgot_password_data["set_password"], token=signup_response.json()["token"]
        ),
        SET_PASSWORD,
    )

    forgot_pass_response = post_request(
        dict(
            forgot_password_data["forgot_password"],
            email=signup_response.json()["email"],
        ),
        FORGOT_PASSWORD,
    )

    assert (
        forgot_pass_response.status_code == OK
    ), f"Expected status code {OK}, but got {forgot_pass_response.status_code}: {forgot_pass_response.text}"

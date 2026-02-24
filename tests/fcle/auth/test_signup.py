import pytest

from conftest import post_request
from fixtures.auth.fixture_signup import OK, SIGNUP, TOO_MANY_REQUESTS, signup_params
from utils.fake_data_generators import generate_email


@pytest.mark.signup
def test_post_api_auth_signup_edge_cases(post_request, signup_params):
    """
    Test the signup API endpoint with edge cases.

    This test verifies the behavior of the signup endpoint for various input combinations,
    including invalid, empty, or edge case inputs for email and language parameters.

    Args:
        post_request (callable): Fixture providing a function to make HTTP POST requests.
        signup_params (tuple): Fixture providing parameterized test data (email, lang, expected_status).

    The test performs the following steps:
        - Sends a POST request to the signup endpoint with the provided email and language.
        - Asserts that the response status code matches the expected status code.
        - For successful responses (status code 200), verifies that the response JSON contains
          the expected email and language values.

    Assertions:
        - The response status code must match the expected status code from `signup_params`.
        - For status code 200, the response JSON's 'email' field must match the input email.
        - For status code 200, the response JSON's 'lang' field must match the input language.

    Fails if:
        - The status code does not match the expected value, including the response text in the error message.
        - The response JSON's email or language does not match the input values for successful responses.
    """

    email, lang, expected_status = signup_params

    response = post_request({"email": email, "lang": lang}, SIGNUP)

    assert (
        response.status_code == expected_status
    ), f"Expected status code {expected_status}, but got {response.status_code}: {response.text}"

    if response.status_code == OK:
        assert (
            response.json()["email"] == email
        ), f"Expected email {email}, but got {response.json()['email']}"
        assert (
            response.json()["lang"] == lang
        ), f"Expected language {lang}, but got {response.json()['lang']}"


@pytest.mark.signup
def test_post_api_auth_signup_duplicate_email(post_request):
    """
    Test the signup API endpoint with a duplicate email.

    This test verifies that attempting to register with an email that has already been used
    results in a 429 status code, indicating a rate-limiting or duplicate registration error.

    Args:
        post_request (callable): Fixture providing a function to make HTTP POST requests.

    The test performs the following steps:
        - Generates a payload with a unique email (using `generate_email`) and language set to 'en'.
        - Sends a POST request to the signup endpoint with the payload (first signup attempt).
        - Sends a second POST request to the signup endpoint with the same payload (duplicate email).
        - Asserts that the second response has a status code of 429.

    Assertions:
        - The second response status code must be 429, indicating a duplicate email error.

    Fails if:
        - The second response status code is not 429, including the response text in the error message.

    Note:
        - Assumes the `generate_email` function from `utils.fake_data_generators` provides a unique email.
        - The test expects a 429 status code for duplicate registrations, as specified in the assertion,
          despite the docstring mentioning a 409 status code, which may indicate a documentation error.
    """

    payload = {
        "email": generate_email(),
        "lang": "en",
    }

    post_request(payload, SIGNUP)

    second_response = post_request(payload, SIGNUP)

    assert (
        second_response.status_code == TOO_MANY_REQUESTS
    ), f"Expected status code 429 for duplicate email, but got {second_response.status_code}: {second_response.text}"

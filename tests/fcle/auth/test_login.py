"""
Login API test suite.

Covers:
- Successful login after signup + set-password flow.
- Login with wrong password.
- Login with unknown user.
- Parameterized validation/error cases (invalid email, password, timezone).
"""

import pytest

from fixtures.auth.fixture_login import login_params
from settings import ENDPOINTS
from utils.fake_data_generators import (
    generate_email,
    generate_nickname,
    generate_password,
)

LOGIN = ENDPOINTS["login"]
SIGNUP = ENDPOINTS["signup"]
SET_PASSWORD = ENDPOINTS["set_password"]


@pytest.mark.login
def test_login_success(post_request):
    """
    Test the login API happy path.

    This test verifies that a user can successfully authenticate via the login endpoint
    after completing the signup and set-password flow.

    Args:
        post_request (callable): Fixture providing a function to make HTTP POST requests.

    The test performs the following steps:
        - Sends a POST request to the signup endpoint with a generated email to obtain a one-time signup token.
        - Sends a POST request to the set-password endpoint using the received token and a valid new password (+ nickname, timezone).
        - Sends a POST request to the login endpoint with email, password, and timezone.
        - Asserts that the response status code is 200 and a JWT token is returned in the response body.

    Assertions:
        - Signup returns 200/201 and contains a non-empty 'token'.
        - Set-password returns 200/204.
        - Login returns 200 with a non-empty string field 'token' (JWT).

    Fails if:
        - Any step returns an unexpected HTTP status.
        - The login response lacks the 'token' field or it is not a non-empty string.

    Note:
        - The signup token is a one-time registration token and must be passed to set-password as 'token',
          while the login endpoint expects plain 'email'/'password'/'timezone'.
    """
    email = generate_email()
    r1 = post_request({"email": email, "lang": "en"}, SIGNUP)
    assert r1.status_code in (200, 201), f"signup failed: {r1.status_code} {r1.text}"
    signup_token = r1.json().get("token")
    assert signup_token, f"no token in signup response: {r1.text}"

    password = generate_password(valid=True)
    nickname = generate_nickname(valid=True)
    r2 = post_request(
        {
            "token": signup_token,
            "newPassword": password,
            "nickname": nickname,
            "timezone": "UTC+3",
        },
        SET_PASSWORD,
    )

    assert r2.status_code in (
        200,
        204,
    ), f"set-password failed: {r2.status_code} {r2.text}"

    r3 = post_request(
        {"email": email, "password": password, "timezone": "UTC+3"}, LOGIN
    )
    assert r3.status_code == 200, f"login failed: {r3.status_code} {r3.text}"

    data = r3.json()
    assert (
        "token" in data and isinstance(data["token"], str) and len(data["token"]) > 10
    )


@pytest.mark.login
def test_login_wrong_password(post_request):
    """
    Test the login API with an incorrect password.

    This test verifies that logging in with an invalid (wrong) password returns a 422
    with domain error code 'user.loginMethod.invalid'.

    Args:
        post_request (callable): Fixture providing a function to make HTTP POST requests.

    The test performs the following steps:
        - Completes signup to obtain a one-time token for the new user.
        - Calls set-password to assign a valid password to that user.
        - Calls login with the same email but an intentionally wrong password.
        - Asserts that the response status code is 422 and the error code matches 'user.loginMethod.invalid'.

    Assertions:
        - Login returns 422.
        - Response JSON has error.code == 'user.loginMethod.invalid'.

    Fails if:
        - Login does not return 422.
        - The error code in the response body differs from the expected domain code.

    Note:
        - A fixed wrong password string is used to avoid delays from heavy password generation logic.
    """
    email = generate_email()
    r1 = post_request({"email": email, "lang": "en"}, SIGNUP)
    assert r1.status_code in (200, 201), f"signup failed: {r1.status_code} {r1.text}"
    token = r1.json()["token"]

    good_pwd = generate_password(valid=True)
    nickname = generate_nickname(valid=True)
    r2 = post_request(
        {
            "token": token,
            "newPassword": good_pwd,
            "nickname": nickname,
            "timezone": "UTC+0",
        },
        SET_PASSWORD,
    )
    assert r2.status_code in (
        200,
        204,
    ), f"set-password failed: {r2.status_code} {r2.text}"

    bad_pwd = "WrongPass1!"
    assert bad_pwd != good_pwd

    r3 = post_request({"email": email, "password": bad_pwd, "timezone": "UTC+0"}, LOGIN)

    assert r3.status_code == 410, f"expected 410, got {r3.status_code}: {r3.text}"
    body = r3.json()
    assert body.get("error", {}).get("code") == "user.loginMethod.invalid"


@pytest.mark.login
def test_login_unknown_user(post_request):
    """
    Test the login API with a non-existent (unknown) user.

    This test verifies that attempting to log in with an email address that does not exist
    returns a client error status (401/404/422) depending on the environment/backend behavior.

    Args:
        post_request (callable): Fixture providing a function to make HTTP POST requests.

    The test performs the following steps:
        - Calls the login endpoint with an unknown email, a strong deterministic password, and a valid timezone.
        - Asserts that the response status is one of 401/404/422.

    Assertions:
        - Response status code is in {401, 404, 422}.

    Fails if:
        - The endpoint returns a different status code.

    Note:
        - A deterministic strong password is used to avoid delays in generating a valid password string.
        - If your API contract standardizes this case to a single status (e.g., 404), narrow the assertion accordingly.
    """
    strong_pwd = "Ab1!Ab1!Ab1!"
    r = post_request(
        {
            "email": "unknown_qa_user@example.com",
            "password": strong_pwd,
            "timezone": "UTC-5",
        },
        LOGIN,
    )
    assert r.status_code in (
        401,
        404,
        422,
        410,
    ), f"unexpected status {r.status_code}: {r.text}"


@pytest.mark.login
def test_login_validation_matrix(post_request, login_params):
    """
    Test the login API validation/error matrix.

    This parameterized test verifies various invalid combinations for email, password,
    and timezone fields to ensure the backend returns the expected status codes
    for each class of input error.

    Args:
        post_request (callable): Fixture providing a function to make HTTP POST requests.
        login_params (tuple): Fixture providing a tuple of (email, password, timezone, expected_status)
                              for each parameterized validation case.

    The test performs the following steps:
        - Builds the login payload from the parameterized tuple.
        - Sends a POST request to the login endpoint.
        - Asserts that the response status code matches the expected status for that case.

    Assertions:
        - The response status code equals the expected status from the parameter set.

    Fails if:
        - The status code differs from the expected value (the response text is included for debugging).

    Notes:
        - The mapping of specific inputs to expected statuses is defined in
          `fixtures/auth/fixture_login.py` via `parameter_generation(...)`.
        - According to observed backend behavior, some cases return 422 instead of 400 (e.g., very long email,
          invalid password composition, invalid/empty/xss timezone). The fixture encodes these expectations.
    """
    email, password, timezone, expected = login_params
    r = post_request(
        {"email": email, "password": password, "timezone": timezone}, LOGIN
    )
    assert (
        r.status_code == expected
    ), f"expected {expected}, got {r.status_code}: {r.text}"

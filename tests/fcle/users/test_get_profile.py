"""
Get-Profile API test suite.

Covers:
- Successful profile retrieval with a valid token.
- Unauthorized access when no token is provided.
- Unauthorized access when a malformed/invalid token is provided.
"""

import pytest

from settings import ENDPOINTS

OK = 200
UNAUTHORIZED = (401, 403)
PROFILE_INFO = ("id", "email", "nickname", "timezone", "joinDate", "lastLogin")


@pytest.mark.get_profile
def test_get_profile_success(auth_headers, get_profile):
    """
    Test the get-profile API happy path.

    This test verifies that an authenticated user can successfully retrieve their profile
    information by providing a valid Authorization header.

    Args:
        get_request (callable): Fixture providing a function to make HTTP GET requests.
        auth_headers (tuple): Fixture returning (headers, email) for an authenticated user.

    The test performs the following steps:
        - Calls the get-profile endpoint with a valid Authorization header.
        - Asserts that the response status code is 200.
        - Verifies that all mandatory fields (id, email, nickname, timezone, joinDate, lastLogin)
          are present in the response body.
        - Ensures field types are correct:
            * id is a positive integer.
            * email is a non-empty string matching the authenticated user's email.
            * hobbies, interests, userLanguages are lists (or null/empty list).

    Assertions:
        - Status code == 200.
        - All mandatory fields exist in the response JSON.
        - Data types and values are correct.

    Fails if:
        - Status code is not 200.
        - Required fields are missing.
        - Field values have unexpected types or do not match expectations.
    """

    headers, email = auth_headers

    body = get_profile(headers)

    for key in PROFILE_INFO:
        assert key in body, f"Missing field '{key}' in response {body}"

    assert isinstance(body["id"], int) and body["id"] > 0
    assert isinstance(body["email"], str) and body["email"], "email must be not-empty"
    assert body["email"].lower() == email.lower()

    hobbies = body.get("hobbies") or []
    interests = body.get("interests") or []
    languages = body.get("userLanguages") or []

    assert isinstance(hobbies, list), f"hobbies must be list or null, got {hobbies}"
    assert isinstance(
        interests, list
    ), f"interests must be list or null, got {interests}"
    assert isinstance(
        languages, list
    ), f"userLanguages must be list or null, got {languages}"


@pytest.mark.get_profile
def test_get_profile_unauthorized_no_token(get_request):
    """
    Test the get-profile API without Authorization header.

    This test verifies that requesting the profile without providing
    an Authorization header results in an unauthorized error.

    Args:
        get_request (callable): Fixture providing a function to make HTTP GET requests.

    The test performs the following steps:
        - Calls the get-profile endpoint without any headers.
        - Asserts that the response status code is 401 Unauthorized.

    Assertions:
        - Status code == 401.

    Fails if:
        - Endpoint returns any other status code.
    """
    r = get_request(ENDPOINTS["get-profile"])
    assert (
        r.status_code == UNAUTHORIZED[0]
    ), f"Expected {UNAUTHORIZED}, got {r.status_code}: {r.text}"


@pytest.mark.get_profile
def test_get_profile_unauthorized_bad_token(get_request, auth_headers):
    """
    Test the get-profile API with an invalid Authorization token.

    This test verifies that modifying the token (making it invalid)
    leads to unauthorized access.

    Args:
        get_request (callable): Fixture providing a function to make HTTP GET requests.
        auth_headers (tuple): Fixture returning (headers, email) for an authenticated user.

    The test performs the following steps:
        - Takes a valid Authorization header and corrupts the token.
        - Calls the get-profile endpoint with the invalid token.
        - Asserts that the response status code is either 401 or 403.

    Assertions:
        - Status code in {401, 403}.

    Fails if:
        - The endpoint returns any other status code.
    """

    headers, _ = auth_headers

    bad = headers["Authorization"][:-1] + "x"
    r1 = get_request(ENDPOINTS["get-profile"], headers={"Authorization": bad})
    assert (
        r1.status_code in UNAUTHORIZED
    ), f"Expected {UNAUTHORIZED}, got {r1.status_code}: {r1.text}"

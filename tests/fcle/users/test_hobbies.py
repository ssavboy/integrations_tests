"""
Users/hobbies API test suite.

Covers:
- Successful adding of hobbies by an authenticated user.
- Attempt to add hobbies without authentication (unauthorized user).
"""

from http import HTTPStatus
from random import sample

import pytest

from parametrs.parameters_hobbies_interests import parameters_hobbies
from settings import CONFLICT, ENDPOINTS


@pytest.mark.hobbies
def test_put_hobbies_success(post_request, get_profile, auth_headers):
    """
    Test the hobbies API happy path.

    This test verifies that an authenticated user can successfully add hobbies
    via the `Users/hobbies` endpoint and later see them in their profile.

    Args:
        post_request (callable): Fixture for sending HTTP PUT requests.
        get_request (callable): Fixture for sending HTTP GET requests.
        auth_headers (tuple): Fixture returning (headers, email) with a valid JWT.

    The test performs the following steps:
        - Uses `auth_headers` to authenticate a new user.
        - Sends a PUT request to `Users/hobbies` with a valid list of hobby IDs.
        - Asserts that the response status code is 200 or 201.
        - Sends a GET request to `Users/get-profile` with the same headers.
        - Asserts that the response status code is 200.
        - Asserts that the `hobbies` field in the profile response exists and is a list.

    Assertions:
        - PUT /Users/hobbies returns 200/201.
        - GET /Users/get-profile returns 200.
        - The `hobbies` field is present in the response body and has type `list`.

    Fails if:
        - PUT does not return 200/201.
        - GET does not return 200.
        - `hobbies` is missing or has an unexpected type.
    """
    headers, _email = auth_headers
    hobbies = sample(parameters_hobbies(valid=True), 5)

    payload = {"hobbies": hobbies}
    r = post_request(payload, ENDPOINTS["hobbies"], headers=headers)
    assert r.status_code in (
        HTTPStatus.OK,
        HTTPStatus.CREATED,
    ), f"Expected 200/201, got {r.status_code}: {r.text}"

    body = get_profile(headers)
    hobbies = body.get("hobbies")

    assert set(payload["hobbies"]).issubset(
        set(hobbies)
    ), f"Expected {set(payload['hobbies'])} in hobbies, got {hobbies}"


@pytest.mark.hobbies
def test_put_invalid_hobbies_success(post_request, auth_headers):
    """
    Test the hobbies API with an incorrect payload.

    Args:
        post_request (callable): Fixture for sending HTTP PUT requests.
        auth_headers (tuple): Fixture returning (headers, email) with a valid JWT.

    The test performs the following steps:
        - Uses `auth_headers` to authenticate a new user.
        - Sends a PUT request to `Users/hobbies` with a invalid string type data.
        - Asserts that the response status code is 400.

    Assertions:
        - PUT /Users/hobbies returns 400.

    Fails if:
        - PUT does return 200.
    """
    headers, _email = auth_headers
    hobbies = ["bad request", "po-po-po"]

    payload = {"hobbies": hobbies}
    r = post_request(payload, ENDPOINTS["hobbies"], headers=headers)
    assert r.status_code == CONFLICT, f"Expected 400, got {r.status_code}: {r.text}"


@pytest.mark.hobbies
def test_unauthorized_user_hobbies(post_request):
    """
    Test the hobbies API with an unauthorized user.

    This test verifies that attempting to add hobbies without authentication
    (no Authorization header) fails with 401 Unauthorized.

    Args:
        post_request (callable): Fixture for sending HTTP PUT requests.

    The test performs the following steps:
        - Sends a PUT request to `Users/hobbies` without headers.
        - Asserts that the response status code is 401 Unauthorized.

    Assertions:
        - PUT /Users/hobbies returns 401.

    Fails if:
        - The status code is not 401.
    """

    hobbies = sample(parameters_hobbies(valid=True), 5)
    payload = {"hobbies": hobbies}

    r = post_request(payload, ENDPOINTS["hobbies"], headers=None)
    assert (
        r.status_code == HTTPStatus.UNAUTHORIZED
    ), f"Expected 401, got {r.status_code}: {r.text}"


# TODO: тест корректный будем ждать когда добавят валидацию на бэк
# @pytest.mark.hobbies
# def test_max_accepted_hobbies(post_request, auth_headers):
#     """
#     Test the maximum accepted hobbies constraint.

#     This test verifies that the API enforces a limit on how many hobbies
#     a user can select at once.

#     Args:
#         post_request (callable): Fixture for sending HTTP POST requests.
#         auth_headers (tuple): Fixture returning (headers, email) with a valid JWT.

#     Steps:
#         - Authenticates a new user.
#         - Sends a POST request to `Users/hobbies` with 6 hobby IDs (exceeding the limit of 5).
#         - Expects the API to reject the request due to exceeding the maximum allowed.

#     Assertions:
#         - Response status code is 422 Unprocessable Entity.

#     Fails if:
#         - API accepts more than the allowed maximum.
#         - Response status is not 422.
#     """

#     headers, _email = auth_headers
#     hobbies = sample(parameters_hobbies(valid=True), 6)

#     payload = {"hobbies": hobbies}
#     r = post_request(payload, ENDPOINTS["hobbies"], headers=headers)

#     assert (
#         r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
#     ), f"Expected 422, got {r.status_code}: {r.text}"


@pytest.mark.hobbies
def test_clear_hobbies_with_empty_list(post_request, auth_headers, get_profile):
    """
    Test clearing hobbies by sending an empty list.

    This test verifies that sending an empty list to the `Users/hobbies` endpoint
    removes all previously set hobbies in the user's profile.

    Args:
        post_request (callable): Fixture for sending HTTP POST requests.
        auth_headers (tuple): Fixture returning (headers, email) with a valid JWT.
        get_profile (callable): Fixture for fetching the user's profile with 200-assert.

    Steps:
        - Sets initial hobbies via POST /Users/hobbies.
        - Verifies that they appear in get-profile.
        - Sends a POST with an empty list to `Users/hobbies`.
        - Verifies that get-profile now returns an empty hobbies list.

    Assertions:
        - Initial POST returns 200 and hobbies are correctly saved.
        - Second POST (with empty list) returns 200.
        - get-profile response contains `hobbies == []`.

    Fails if:
        - Either POST does not return 200.
        - get-profile does not reflect the changes.
    """

    headers, _email = auth_headers
    hobbies = sample(parameters_hobbies(valid=True), 5)

    payload = {"hobbies": hobbies}

    r = post_request(payload, ENDPOINTS["hobbies"], headers)
    assert (
        r.status_code == HTTPStatus.OK
    ), f"Expected 200, got {r.status_code}: {r.text}"

    body = get_profile(headers)
    assert (
        payload["hobbies"] == body["hobbies"]
    ), f"Expected {payload} in body, got {body}"

    clear_payload = {"hobbies": []}
    r = post_request(clear_payload, ENDPOINTS["hobbies"], headers)
    assert (
        r.status_code == HTTPStatus.OK
    ), f"Expected 200, got {r.status_code}: {r.text}"

    body = get_profile(headers)
    hobbies = body.get("hobbies")
    assert hobbies == [], f"Expected hobbies be empty, got {hobbies}"

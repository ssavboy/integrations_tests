"""
Users/interests API test suite.

Covers:
- Successful adding of interests by an authenticated user.
- Attempt to add interests without authentication (unauthorized user).
"""

from http import HTTPStatus
from random import sample

import pytest

from parametrs.parameters_hobbies_interests import parameters_interests
from settings import CONFLICT, ENDPOINTS

# TODO: валидация от бэка
# @pytest.mark.interests
# def test_put_interests_success(post_request, get_profile, auth_headers):
#     """
#     Test the interests API happy path.

#     This test verifies that an authenticated user can successfully add interests
#     via the `Users/interests` endpoint and later see them in their profile.

#     Args:
#         post_request (callable): Fixture for sending HTTP PUT requests.
#         get_request (callable): Fixture for sending HTTP GET requests.
#         auth_headers (tuple): Fixture returning (headers, email) with a valid JWT.

#     The test performs the following steps:
#         - Uses `auth_headers` to authenticate a new user.
#         - Sends a PUT request to `Users/interests` with a valid list of hobby IDs.
#         - Asserts that the response status code is 200 or 201.
#         - Sends a GET request to `Users/get-profile` with the same headers.
#         - Asserts that the response status code is 200.
#         - Asserts that the `interests` field in the profile response exists and is a list.

#     Assertions:
#         - PUT /Users/interests returns 200/201.
#         - GET /Users/get-profile returns 200.
#         - The `interests` field is present in the response body and has type `list`.

#     Fails if:
#         - PUT does not return 200/201.
#         - GET does not return 200.
#         - `interests` is missing or has an unexpected type.
#     """
#     headers, _email = auth_headers
#     interests = sample(parameters_interests(valid=True), 5)

#     payload = {"interests": interests}
#     r = post_request(payload, ENDPOINTS["interests"], headers=headers)
#     assert r.status_code in (
#         HTTPStatus.OK,
#         HTTPStatus.CREATED,
#     ), f"Expected 200/201, got {r.status_code}: {r.text}"

#     body = get_profile(headers)
#     interests = body.get("interests")

#     assert set(payload["interests"]).issubset(
#         set(interests)
#     ), f"Expected {set(payload['interests'])} in interests, got {interests}"


@pytest.mark.interests
def test_put_invalid_interests_success(post_request, auth_headers):
    """
    Test the interests API with an incorrect payload.

    Args:
        post_request (callable): Fixture for sending HTTP PUT requests.
        auth_headers (tuple): Fixture returning (headers, email) with a valid JWT.

    The test performs the following steps:
        - Uses `auth_headers` to authenticate a new user.
        - Sends a PUT request to `Users/interests` with a invalid string type data.
        - Asserts that the response status code is 400.

    Assertions:
        - PUT /Users/interests returns 400.

    Fails if:
        - PUT does return 200.
    """
    headers, _email = auth_headers
    interests = ["bad request", "po-po-po"]

    payload = {"interests": interests}
    r = post_request(payload, ENDPOINTS["interests"], headers=headers)
    assert r.status_code == CONFLICT, f"Expected 400, got {r.status_code}: {r.text}"


@pytest.mark.interests
def test_unauthorized_user_interests(post_request):
    """
    Test the interests API with an unauthorized user.

    This test verifies that attempting to add interests without authentication
    (no Authorization header) fails with 401 Unauthorized.

    Args:
        post_request (callable): Fixture for sending HTTP PUT requests.

    The test performs the following steps:
        - Sends a PUT request to `Users/interests` without headers.
        - Asserts that the response status code is 401 Unauthorized.

    Assertions:
        - PUT /Users/interests returns 401.

    Fails if:
        - The status code is not 401.
    """

    interests = sample(parameters_interests(valid=True), 5)
    payload = {"interests": interests}

    r = post_request(payload, ENDPOINTS["interests"], headers=None)
    assert (
        r.status_code == HTTPStatus.UNAUTHORIZED
    ), f"Expected 401, got {r.status_code}: {r.text}"


# TODO: ждем апдейта валидаци
# @pytest.mark.interests
# def test_max_accepted_interests(post_request, auth_headers):
#     """
#     Test the maximum accepted interests constraint.

#     This test verifies that the API enforces a limit on how many interests
#     a user can select at once.

#     Args:
#         post_request (callable): Fixture for sending HTTP POST requests.
#         auth_headers (tuple): Fixture returning (headers, email) with a valid JWT.

#     Steps:
#         - Authenticates a new user.
#         - Sends a POST request to `Users/interests` with 6 hobby IDs (exceeding the limit of 5).
#         - Expects the API to reject the request due to exceeding the maximum allowed.

#     Assertions:
#         - Response status code is 422 Unprocessable Entity.

#     Fails if:
#         - API accepts more than the allowed maximum.
#         - Response status is not 422.
#     """

#     headers, _email = auth_headers
#     interests = sample(parameters_interests(valid=True), 6)

#     payload = {"interests": interests}
#     r = post_request(payload, ENDPOINTS["interests"], headers=headers)

#     assert (
#         r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
#     ), f"Expected 422, got {r.status_code}: {r.text}"


@pytest.mark.interests
def test_clear_interests_with_empty_list(post_request, auth_headers, get_profile):
    """
    Test clearing interests by sending an empty list.

    This test verifies that sending an empty list to the `Users/interests` endpoint
    removes all previously set interests in the user's profile.

    Args:
        post_request (callable): Fixture for sending HTTP POST requests.
        auth_headers (tuple): Fixture returning (headers, email) with a valid JWT.
        get_profile (callable): Fixture for fetching the user's profile with 200-assert.

    Steps:
        - Sets initial interests via POST /Users/interests.
        - Verifies that they appear in get-profile.
        - Sends a POST with an empty list to `Users/interests`.
        - Verifies that get-profile now returns an empty interests list.

    Assertions:
        - Initial POST returns 200 and interests are correctly saved.
        - Second POST (with empty list) returns 200.
        - get-profile response contains `interests == []`.

    Fails if:
        - Either POST does not return 200.
        - get-profile does not reflect the changes.
    """

    headers, _email = auth_headers
    interests = sample(parameters_interests(valid=True), 5)

    payload = {"interests": interests}

    r = post_request(payload, ENDPOINTS["interests"], headers)
    assert (
        r.status_code == HTTPStatus.OK
    ), f"Expected 200, got {r.status_code}: {r.text}"

    body = get_profile(headers)
    assert (
        payload["interests"] == body["interests"]
    ), f"Expected {payload} in body, got {body}"

    clear_payload = {"interests": []}
    r = post_request(clear_payload, ENDPOINTS["interests"], headers)
    assert (
        r.status_code == HTTPStatus.OK
    ), f"Expected 200, got {r.status_code}: {r.text}"

    body = get_profile(headers)
    interests = body.get("interests")
    assert interests == [], f"Expected interests be empty, got {interests}"

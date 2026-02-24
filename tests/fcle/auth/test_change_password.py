import pytest

from conftest import post_request
from fixtures.auth.fixture_change_password import (
    CHANGE_PASSWORD,
    OK,
    SET_PASSWORD,
    SIGNUP,
    change_password_data,
)
from settings import ENDPOINTS


@pytest.mark.change_password
def test_post_api_auth_change_password(post_request, change_password_data):
    """
    Test successful password change through the API change password endpoint.

    This test validates the complete password change workflow:
    1. User registration via signup endpoint
    2. Initial password setup
    3. User authentication via login
    4. Password change with valid credentials

    Args:
        post_request (callable): Fixture for making HTTP POST requests
        change_password_data (dict): Test data containing payloads for signup,
                                   set_password, and change_password endpoints

    Steps:
        - Register new user with signup endpoint
        - Set initial password using the registration token
        - Login to obtain JWT authentication token
        - Change password using valid current password
        - Verify successful response (HTTP 200)

    Assertions:
        - All intermediate steps return HTTP 200 status
        - Final password change returns HTTP 200 status

    Error Handling:
        - Includes detailed error messages in assertions for debugging
    """

    signup_response = post_request(change_password_data["signup"], SIGNUP)
    assert signup_response.status_code == OK, f"Signup failed: {signup_response.text}"

    signup_data = signup_response.json()
    token = signup_data["token"]
    email = signup_data["email"]

    set_password_payload = dict(change_password_data["set_password"], token=token)
    set_password_response = post_request(set_password_payload, SET_PASSWORD)
    assert (
        set_password_response.status_code == OK
    ), f"Set password failed: {set_password_response.text}"

    login_response = post_request(
        {
            "email": email,
            "password": change_password_data["set_password"]["newPassword"],
            "timezone": "UTC",
        },
        ENDPOINTS["login"],
    )
    assert login_response.status_code == OK, f"Login failed: {login_response.text}"
    jwt_token = login_response.json()["token"]

    headers = {"Authorization": f"Bearer {jwt_token}"}

    current_password = change_password_data["set_password"]["newPassword"]
    change_password_payload = dict(
        change_password_data["change_password"],
        oldPassword=current_password,
        email=email,
    )

    change_password_response = post_request(
        change_password_payload, CHANGE_PASSWORD, headers=headers
    )

    assert (
        change_password_response.status_code == OK
    ), f"Expected status code {OK}, but got {change_password_response.status_code}: {change_password_response.text}"


@pytest.mark.change_password
def test_post_api_auth_change_password_wrong_old_password(
    post_request, change_password_data
):
    """
    Test password change endpoint with incorrect old password.

    This test verifies that the API properly rejects password change attempts
    when the provided old password doesn't match the user's current password.

    Args:
        post_request (callable): Fixture for making HTTP POST requests
        change_password_data (dict): Test data containing payloads for signup,
                                   set_password, and change_password endpoints

    Steps:
        - Register new user and set initial password
        - Authenticate to obtain JWT token
        - Attempt password change with incorrect old password
        - Verify API returns appropriate error status (400, 401, or 422)

    Assertions:
        - Password change attempt with wrong credentials returns error status
        - Error status is one of: 400 (Bad Request), 401 (Unauthorized), or 422 (Unprocessable Entity)

    Error Handling:
        - Includes assertion message with actual vs expected status codes
    """

    signup_response = post_request(change_password_data["signup"], SIGNUP)
    assert signup_response.status_code == OK, f"Signup failed: {signup_response.text}"

    signup_data = signup_response.json()
    token = signup_data["token"]
    email = signup_data["email"]

    set_password_payload = dict(change_password_data["set_password"], token=token)
    set_password_response = post_request(set_password_payload, SET_PASSWORD)
    assert (
        set_password_response.status_code == OK
    ), f"Set password failed: {set_password_response.text}"

    login_response = post_request(
        {
            "email": email,
            "password": change_password_data["set_password"]["newPassword"],
            "timezone": "UTC",
        },
        ENDPOINTS["login"],
    )
    assert login_response.status_code == OK, f"Login failed: {login_response.text}"
    jwt_token = login_response.json()["token"]

    headers = {"Authorization": f"Bearer {jwt_token}"}

    change_password_payload = dict(
        change_password_data["change_password"],
        oldPassword="wrong_password_123",
        email=email,
    )

    change_password_response = post_request(
        change_password_payload, CHANGE_PASSWORD, headers=headers
    )

    assert change_password_response.status_code in [
        400,
        401,
        422,
        410,
    ], f"Expected error status code (400, 401, 422, 410), but got {change_password_response.status_code}"

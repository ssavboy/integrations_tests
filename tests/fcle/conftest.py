from http import HTTPStatus

import pytest
import requests

from settings import BASE_URL, ENDPOINTS, TIMEOUT
from utils.fake_data_generators import (
    generate_email,
    generate_nickname,
    generate_password,
)


@pytest.fixture
def post_request():
    """
    Fixture that provides a function to make HTTP POST requests.

    Returns:
        function: A function that sends a POST request to the specified endpoint with the given payload.

    The inner function `_make_request` has the following parameters:
        payload (dict): The JSON payload to send in the POST request.
        endpoint (str): The endpoint to append to the BASE_URL for the request.

    Returns:
        requests.Response: The response object from the POST request.

    Raises:
        pytest.fail: If the request fails due to a requests.exceptions.RequestException,
                     the test will fail with a message containing the exception details.
    """

    def _make_request(payload, endpoint, headers=None):
        try:
            response = requests.post(
                url=f"{BASE_URL}{endpoint}",
                json=payload,
                headers=headers,
                timeout=TIMEOUT,
            )
            return response
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Request failed: {e}")

    return _make_request


@pytest.fixture
def get_request():
    """
    Fixture that provides a function to make HTTP GET requests.

    Returns:
        function: A function that sends a GET request to the specified endpoint
                  with optional query parameters and headers.

    The inner function `_make_request` has the following parameters:
        endpoint (str): The endpoint to append to the BASE_URL for the request.
        params (dict, optional): Dictionary of URL query parameters to include in the request.
        headers (dict, optional): Dictionary of HTTP headers to include in the request.

    Returns:
        requests.Response: The response object from the GET request.

    Raises:
        pytest.fail: If the request fails due to a requests.exceptions.RequestException,
                     the test will fail with a message containing the exception details.
    """

    def _make_request(endpoint, params=None, headers=None):
        try:
            response = requests.get(
                url=f"{BASE_URL}{endpoint}",
                params=params,
                headers=headers,
                timeout=TIMEOUT,
            )
            return response
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Request failed: {e}")

    return _make_request


@pytest.fixture
def put_request():
    """
    Fixture that provides a function to make HTTP PUT requests.

    Returns:
        function: A function that sends a PUT request to the specified endpoint with the given payload.

    The inner function `_make_request` has the following parameters:
        payload (dict): The JSON payload to send in the PUT request.
        endpoint (str): The endpoint to append to the BASE_URL for the request.

    Returns:
        requests.Response: The response object from the PUT request.

    Raises:
        pytest.fail: If the request fails due to a requests.exceptions.RequestException,
                     the test will fail with a message containing the exception details.
    """

    def _make_request(payload, endpoint, headers=None):
        try:
            response = requests.put(
                url=f"{BASE_URL}{endpoint}",
                json=payload,
                headers=headers,
                timeout=TIMEOUT,
            )
            return response
        except requests.exceptions.RequestException as e:
            pytest.fail(f"request failed: {e}")

    return _make_request


@pytest.fixture
def delete_request():
    """
    Fixture that provides a function to make HTTP DELETE requests.

    Returns:
        function: A function `_make_request` that sends a DELETE request to
                  the specified endpoint with optional headers and payload.

    The inner function `_make_request` has the following parameters:
        endpoint (str): The endpoint to append to the BASE_URL for the request.
        headers (dict, optional): Dictionary of HTTP headers to include in the request.
        payload (dict, optional): JSON body to include in the request (if required).

    Returns:
        requests.Response: The response object from the DELETE request.

    Raises:
        pytest.fail: If the request fails due to a requests.exceptions.RequestException,
                     the test will fail with a message containing the exception details.
    """

    def _make_request(payload, endpoint, headers=None):
        try:
            response = requests.delete(
                url=f"{BASE_URL}{endpoint}",
                json=payload,
                headers=headers,
                timeout=TIMEOUT,
            )
            return response
        except requests.exceptions.RequestException as e:
            pytest.fail(f"request failed: {e}")

    return _make_request


@pytest.fixture
def auth_headers(post_request):
    """
    Fixture: Provides Authorization headers for an authenticated user.

    This fixture automates the signup → set-password → login flow to produce
    a valid JWT token for subsequent authenticated requests in tests.

    Steps:
        1. **Signup**: Registers a new user with a generated email.
           - Endpoint: `POST /signup`
           - Expects status 200/201 and a 'token' in response.
        2. **Set Password**: Completes registration by setting password, nickname, and timezone.
           - Endpoint: `POST /set-password`
           - Expects status 200/204.
        3. **Login**: Authenticates the user to obtain a JWT token.
           - Endpoint: `POST /login`
           - Expects status 200 and a response body containing a non-empty 'token'.

    Args:
        post_request (callable): Fixture that performs HTTP POST requests.

    Returns:
        tuple:
            - headers (dict): Authorization header in the format `{"Authorization": "Bearer <jwt>"}`.
            - email (str): The email address used for the test user.

    Assertions:
        - Each step (signup, set-password, login) must return the expected status codes.
        - Signup response must contain a non-empty 'token'.
        - Login response must contain a valid JWT string.
    """

    email = generate_email()
    # signup
    r1 = post_request({"email": email, "lang": "en"}, ENDPOINTS["signup"])
    assert r1.status_code == HTTPStatus.OK, f"Signup failed: {r1.status_code} {r1.text}"
    token_signup = r1.json()["token"]

    # set-password
    pwd = generate_password(valid=True)
    nick = generate_nickname(valid=True)
    r2 = post_request(
        {
            "token": token_signup,
            "newPassword": pwd,
            "nickname": nick,
            "timezone": "UTC+4",
        },
        ENDPOINTS["set_password"],
    )

    assert (
        r2.status_code == HTTPStatus.OK
    ), f"Set password failed: {r2.status_code} {r2.text}"

    # login
    r3 = post_request(
        {"email": email, "password": pwd, "timezone": "UTC+4"}, ENDPOINTS["login"]
    )

    assert r3.status_code == HTTPStatus.OK, f"Login failed: {r3.status_code} {r3.text}"
    jwt = r3.json()["token"]

    return {"Authorization": f"Bearer {jwt}"}, email


@pytest.fixture
def get_profile(get_request):
    """
    Fixture: Provides a helper function to fetch the authenticated user's profile.

    This fixture wraps the `get_request` fixture and standardizes the call to
    the `/Users/get-profile` endpoint. It asserts that the response status code
    is 200 (OK) and returns the parsed JSON body.

    Args:
        get_request (callable): Fixture that performs HTTP GET requests.

    Returns:
        function: A callable `_fetch(headers)` that:
            - Sends a GET request to the `Users/get-profile` endpoint with the provided headers.
            - Asserts that the response status code equals 200.
            - Returns the parsed response JSON as a dict.

    Usage:
        def test_example(auth_headers, get_profile):
            headers, _ = auth_headers
            profile = get_profile(headers)
            assert "id" in profile
            assert profile["email"].endswith("@example.com")

    Fails if:
        - The response status code is not 200.
        - The response body is not valid JSON.
    """

    def _fetch(headers):
        r = get_request(ENDPOINTS["get-profile"], headers=headers)
        assert (
            r.status_code == HTTPStatus.OK
        ), f"Expected status_code 200, got {r.status_code}: {r.text}"
        return r.json()

    return _fetch


@pytest.fixture
def upload_file():
    def _upload_file(data, files, headers, endpoint):
        try:
            return requests.post(
                url=f"{BASE_URL}{endpoint}", data=data, files=files, headers=headers
            )
        except requests.exceptions.RequestException as e:
            pytest.fail(f"request failed: {e}")

    return _upload_file


@pytest.fixture
def upload_file_put():
    def _upload_file(data, files, headers, endpoint, id_):
        try:
            return requests.put(
                url=f"{BASE_URL}{endpoint}/{id_}", data=data, files=files, headers=headers
            )
        except requests.exceptions.RequestException as e:
            pytest.fail(f"request failed: {e}")

    return _upload_file

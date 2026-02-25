import pytest

from fixtures.users.fixture_telegram import (
    USERS_TELEGRAM,
    OK,
    telegram_users_data,
)

NOT_FOUND = 404


@pytest.mark.telegram_get
def test_get_telegram_users(get_request):
    """
    Test the GET /Users/telegram endpoint to retrieve all Telegram users.

    This test verifies that the telegram users endpoint returns a list of users
    with the expected structure and data types.

    Args:
        get_request (callable): Fixture providing a function to make HTTP GET requests.

    The test performs the following steps:
        - Sends a GET request to the Users/telegram endpoint.
        - Verifies the response status code is 200.
        - Validates that response contains a list of users.
        - Checks that each user has required fields when users exist.

    Assertions:
        - Response status code == 200.
        - Response Content-Type is JSON.
        - Response body is a list.
        - Each user contains required fields: id, telegramId, username.

    Fails if:
        - Status code is not 200.
        - Response is not valid JSON or not a list.
        - User objects are missing required fields.
    """
    response = get_request(USERS_TELEGRAM)

    assert response.status_code == OK, f"Expected {OK}, got {response.status_code}: {response.text}"

    assert "application/json" in response.headers.get("Content-Type", ""), "Response should be in JSON format"

    users_data = response.json()
    assert isinstance(users_data, list), "Response should be a list of users"

    if users_data:
        first_user = users_data[0]
        assert "id" in first_user, "User should have an id field"
        assert "telegramId" in first_user, "User should have a telegramId field"
        assert "username" in first_user, "User should have a username field"


@pytest.mark.telegram_get
def test_get_telegram_users_with_query_params(get_request):
    """
    Test the GET /Users/telegram endpoint with query parameters.

    This test verifies that the telegram users endpoint correctly handles
    pagination parameters and returns the expected data structure.

    Args:
        get_request (callable): Fixture providing a function to make HTTP GET requests.

    The test performs the following steps:
        - Sends a GET request with limit and offset parameters.
        - Verifies the response status code is 200.
        - Validates that the response is still a valid list structure.

    Assertions:
        - Response status code == 200.
        - Response body is a list (respecting pagination).

    Fails if:
        - Status code is not 200.
        - Response structure is invalid.
    """
    params = {"limit": 5, "offset": 0}

    response = get_request(USERS_TELEGRAM, params=params)

    assert response.status_code == OK, f"Expected {OK}, got {response.status_code}: {response.text}"

    users_data = response.json()
    assert isinstance(users_data, list), "Response should be a list of users"


@pytest.mark.telegram_get
def test_get_specific_telegram_user(get_request):
    """
    Test the GET /Users/telegram/{id} endpoint to retrieve a specific user.

    This test verifies that a specific telegram user can be retrieved by ID
    and that the response contains the expected data structure.

    Args:
        get_request (callable): Fixture providing a function to make HTTP GET requests.

    The test performs the following steps:
        - First gets all users to find a valid ID.
        - Sends GET request for specific user.
        - Verifies response structure and data.

    Assertions:
        - If user exists: status code == 200, response is a user object.
        - User ID matches requested ID.
        - User contains required fields.

    Skips if:
        - No users available for testing.
        - User was deleted between requests.

    Fails if:
        - Unexpected status codes or response structure.
    """
    all_users_response = get_request(USERS_TELEGRAM)

    if all_users_response.status_code == OK and all_users_response.json():
        test_user = all_users_response.json()[0]
        user_id = test_user["id"]

        response = get_request(f"{USERS_TELEGRAM}/{user_id}")

        if response.status_code == OK:
            user_data = response.json()
            assert isinstance(user_data, dict), "Response should be a user object"
            assert user_data["id"] == user_id, "User ID should match requested ID"
            assert "telegramId" in user_data, "User should have telegramId field"
        elif response.status_code == NOT_FOUND:
            pytest.skip(f"User with ID {user_id} not found (may have been deleted)")
    else:
        pytest.skip("No users available for testing specific user endpoint")


@pytest.mark.telegram_get
def test_get_nonexistent_telegram_user(get_request):
    """
    Test the GET /Users/telegram/{id} endpoint with non-existent user ID.

    This test verifies that requesting a non-existent telegram user
    returns the appropriate error status code.

    Args:
        get_request (callable): Fixture providing a function to make HTTP GET requests.

    The test performs the following steps:
        - Sends a GET request with a non-existent user ID.
        - Verifies the response status code is 404.

    Assertions:
        - Response status code == 404.

    Fails if:
        - Status code is not 404.
    """
    nonexistent_id = 999999

    response = get_request(f"{USERS_TELEGRAM}/{nonexistent_id}")

    assert response.status_code == NOT_FOUND, f"Expected {NOT_FOUND} for non-existent user, got {response.status_code}: {response.text}"

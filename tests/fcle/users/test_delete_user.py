import pytest

from settings import ENDPOINTS

DELETE_USER = ENDPOINTS["users"]
GET_PROFILE = ENDPOINTS["get-profile"]
OK = 200
DELETED = (404, 422, 410)


@pytest.mark.delete_user
def test_delete_user(auth_headers, delete_request, get_request):
    """
    Test the /api/Users DELETE endpoint

    Args:
        auth_headers (dict): Authorization headers fixture
        delete_request (callable): Fixture to perform DELETE requests
        get_request (callable): Fixture to perform PUT requests

    """

    # Signup, set password and login of the test user
    headers, email = auth_headers

    # Delete test user
    r_del = delete_request({"email": email}, DELETE_USER, headers=headers)
    assert (
        r_del.status_code == 200
    ), f"Expected status_code 200, got {r_del.status_code}: {r_del.text}"

    # Validates deleted users
    r_test_del = get_request(ENDPOINTS["get-profile"], headers=headers)
    assert (
        r_test_del.status_code in DELETED
    ), f"Expected status_code {DELETED}, got {r_test_del.status_code}: {r_test_del.text}"

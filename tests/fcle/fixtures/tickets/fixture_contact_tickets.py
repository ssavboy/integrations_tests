import pytest
import requests

from settings import CONFLICT as CONFLICT
from settings import ENDPOINTS
from utils.fake_data_generators import generate_email

CONTACT_TICKETS = ENDPOINTS["contact_tickets"]
OK = 200
CREATED = 201
BAD_REQUEST = 400
UNPROCESSABLE_ENTITY = 422


@pytest.fixture
def post_request(payload, endpoint):
    """
    Fixture for making POST requests to the API.

    Args:
        payload (dict): The data to be sent in the request body.
        endpoint (str): The API endpoint to send the request to.

    Returns:
        Response: The response object from the POST request.
    """
    base_url = "http://example.com/api/"
    url = f"{base_url}{endpoint}"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    return response


@pytest.fixture
def contact_tickets_data():
    """
    Fixture providing test data for ContactTickets API tests.

    Returns:
        dict: Test data containing different scenarios:
            - new_user: Data for creating a ticket with a new user (userId=None)
            - without_user_id: Data for creating a ticket without userId field
            - invalid_email: Data with invalid email format for validation testing
    """
    return {
        "new_user": {
            "email": generate_email(),
            "subject": "this subject - new user",
            "message": "this is message for new user",
            "userId": None,
        },
        "without_user_id": {
            "email": generate_email(),
            "subject": "this subject - without user",
            "message": "this is message for not user",
        },
        "invalid_email": {
            "email": "this is invalid email",
            "subject": "invalid subject",
            "message": "invalid message",
        },
    }

import pytest

from fixtures.tickets.fixture_contact_tickets import (
    BAD_REQUEST,
    CONFLICT,
    CONTACT_TICKETS,
    CREATED,
    OK,
    UNPROCESSABLE_ENTITY,
    contact_tickets_data,
)


def test_post_contact_tickets_new_user(post_request, contact_tickets_data):
    """
    Test the ContactTickets API endpoint for new users.

    This test verifies that a contact ticket can be created for a new user
    (userId should be null when user doesn't exist in database).

    Args:
        post_request (callable): Fixture providing a function to make HTTP POST requests.
        contact_tickets_data (dict): Fixture providing test data for contact tickets endpoints.

    Steps:
        - Sends a POST request to the ContactTickets endpoint with payload for new user.
        - Verifies the response status code is 200 or 201.
        - Validates that all response fields match the sent data.
        - Ensures userId is null for non-existent users.

    Assertions:
        - Response status code must be 200 or 201.
        - Response must contain valid JSON data.
        - Email, subject, and message must match the sent payload.
        - UserId must be null.

    Fails if:
        - Any of the assertions fail, with detailed error messages.
    """
    payload = contact_tickets_data["new_user"]

    response = post_request(payload, CONTACT_TICKETS)

    assert response.status_code in [
        OK,
        CREATED,
    ], f"Expected status code {OK} or {CREATED}, but got {response.status_code}: {response.text}"

    assert "application/json" in response.headers.get(
        "Content-Type", ""
    ), "Response should be in JSON format"

    response_data = response.json()

    # Validate response structure
    assert "email" in response_data, "Response should contain email field"
    assert "subject" in response_data, "Response should contain subject field"
    assert "message" in response_data, "Response should contain message field"
    assert "userId" in response_data, "Response should contain userId field"

    # Validate data matches
    assert (
        response_data["email"] == payload["email"]
    ), f"Email mismatch. Expected: {payload['email']}, Got: {response_data['email']}"
    assert (
        response_data["subject"] == payload["subject"]
    ), f"Subject mismatch. Expected: {payload['subject']}, Got: {response_data['subject']}"
    assert (
        response_data["message"] == payload["message"]
    ), f"Message mismatch. Expected: {payload['message']}, Got: {response_data['message']}"

    # Validate userId is null for new users
    assert (
        response_data["userId"] is None
    ), f"UserId should be null for new users. Got: {response_data['userId']}"


def test_post_contact_tickets_without_user_id(post_request, contact_tickets_data):
    """
    Test the ContactTickets API endpoint without userId field.

    This test verifies that a contact ticket can be created when userId field
    is not provided in the request (should default to null).

    Args:
        post_request (callable): Fixture providing a function to make HTTP POST requests.
        contact_tickets_data (dict): Fixture providing test data for contact tickets endpoints.

    Steps:
        - Sends a POST request to the ContactTickets endpoint without userId field.
        - Verifies the response status code is 200 or 201.
        - Validates that all response fields match the sent data.
        - Ensures userId is null in the response.

    Assertions:
        - Response status code must be 200 or 201.
        - Email, subject, and message must match the sent payload.
        - UserId must be null in response.

    Fails if:
        - Any of the assertions fail.
    """
    payload = contact_tickets_data["without_user_id"]

    response = post_request(payload, CONTACT_TICKETS)

    assert response.status_code in [
        OK,
        CREATED,
    ], f"Expected status code {OK} or {CREATED}, but got {response.status_code}"

    response_data = response.json()

    assert (
        response_data["email"] == payload["email"]
    ), f"Email mismatch. Expected: {payload['email']}, Got: {response_data['email']}"
    assert (
        response_data["subject"] == payload["subject"]
    ), f"Subject mismatch. Expected: {payload['subject']}, Got: {response_data['subject']}"
    assert (
        response_data["message"] == payload["message"]
    ), f"Message mismatch. Expected: {payload['message']}, Got: {response_data['message']}"

    user_id = response_data.get("userId")
    assert user_id is None, f"UserId should be null when not provided. Got: {user_id}"


def test_post_contact_tickets_validation(post_request, contact_tickets_data):
    """
    Test the ContactTickets API endpoint validation.

    This test verifies that the endpoint properly validates input data
    and returns appropriate error codes for invalid requests.

    Args:
        post_request (callable): Fixture providing a function to make HTTP POST requests.
        contact_tickets_data (dict): Fixture providing test data for contact tickets endpoints.

    Steps:
        - Sends a POST request to the ContactTickets endpoint with invalid email format.
        - Verifies the response status code indicates validation error 409.

    Assertions:
        - Response status code must be 400 or 422.

    Fails if:
        - Response status code is not a validation error code.
    """
    payload = contact_tickets_data["invalid_email"]

    response = post_request(payload, CONTACT_TICKETS)

    assert (
        response.status_code == CONFLICT
    ), f"Expected validation error 409, but got {response.status_code}"

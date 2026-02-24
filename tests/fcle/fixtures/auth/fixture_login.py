"""
Pytest fixture for login parameterization.

This module defines parameterized test cases for the login endpoint.
Each test case is generated using the `parameter_generation` function,
which builds request payloads with various combinations of email, password,
timezone, and expected HTTP status codes.
"""

import pytest

from parametrs.parameters_login import parameter_generation
from settings import CONFLICT, ENDPOINTS

LOGIN = ENDPOINTS["login"]
OK = 200

# -------------------------------------------------------------------
# List of test parameters for login scenarios.
# Each parameter is generated via parameter_generation:
#   - email: valid / invalid / empty / xss / long
#   - password: valid / invalid / empty / xss
#   - timezone: valid / invalid / empty / xss
#   - expected HTTP status code
#
# This matrix allows validation of:
#   - incorrect or missing email
#   - incorrect or missing password
#   - incorrect or missing timezone
#   - valid requests
# -------------------------------------------------------------------
PARAMS = [
    parameter_generation("invalid", "valid", "valid", CONFLICT),  # invalid email
    parameter_generation("empty", "valid", "valid", CONFLICT),  # empty email
    parameter_generation("xss", "valid", "valid", CONFLICT),  # email with XSS payload
    parameter_generation("long", "valid", "valid", 410),  # excessively long email
    parameter_generation("valid", "empty", "valid", CONFLICT),  # empty password
    parameter_generation("valid", "invalid", "valid", 410),  # invalid password
    parameter_generation("valid", "xss", "valid", 410),  # password with XSS payload
    parameter_generation("valid", "valid", "invalid", 410),  # invalid timezone
    parameter_generation("valid", "valid", "empty", 410),  # empty timezone
    parameter_generation("valid", "valid", "xss", 410),  # timezone with XSS payload
]

# -------------------------------------------------------------------
# IDs for pytest parameterization.
# These IDs are human-readable and appear in test reports,
# e.g.: email=valid,password=empty,timezone=valid,status=400
# -------------------------------------------------------------------
IDS = [
    f"email={email},password={password},timezone={tz},status={status}"
    for (email, password, tz, status) in PARAMS
]


@pytest.fixture(params=PARAMS, ids=IDS)
def login_params(request):
    """
    Pytest fixture for login test parameterization.

    This fixture provides different combinations of
    (email, password, timezone, expected_status) for login testing.

    Args:
        request (FixtureRequest): Pytest request object containing
            the currently selected parameter.

    Yields:
        tuple[str, str, str, int]:
        - email (str): Email value (valid/invalid/empty/xss/long).
        - password (str): Password value (valid/invalid/empty/xss).
        - timezone (str): Timezone value (valid/invalid/empty/xss).
        - expected_status (int): Expected HTTP response status code.
    """
    return request.param

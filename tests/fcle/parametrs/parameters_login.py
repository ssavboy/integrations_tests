"""
Utility for generating parameter sets for /api/Auth/login tests.

This module provides the `parameter_generation` function, which
constructs test parameters for different login scenarios by
combining variations of email, password, and timezone fields.
"""

import random

from utils.fake_data_generators import generate_email, generate_password


def parameter_generation(email_type, password_type, timezone_type, expected_status):
    """
    Build a parameter set for the /api/Auth/login endpoint.

    Args:
        email_type (str): Type of email to generate. One of:
            - "valid"   → randomly generated valid email
            - "invalid" → invalid email string
            - "empty"   → empty string
            - "long"    → excessively long email address
            - "xss"     → XSS injection payload
            - "unknown" → random valid-looking but unregistered email
        password_type (str): Type of password to generate. One of:
            - "valid"   → randomly generated valid password
            - "invalid" → randomly generated invalid password
            - "empty"   → empty string
            - "short"   → deliberately too short password
            - "xss"     → XSS injection payload
            - "wrong"   → valid password, but assumed incorrect for user
        timezone_type (str): Type of timezone to use. One of:
            - "valid"   → random UTC offset (−12 to +14)
            - "invalid" → invalid timezone (e.g. UTC-16)
            - "empty"   → empty string
            - "xss"     → XSS injection payload
        expected_status (int): Expected HTTP response status code.

    Returns:
        tuple[str, str, str, int]:
        - email (str): Email value according to `email_type`.
        - password (str): Password value according to `password_type`.
        - timezone (str): Timezone value according to `timezone_type`.
        - expected_status (int): The expected HTTP status code.

    Raises:
        ValueError: If an unknown type is provided for email, password,
            or timezone.
    """

    email_map = {
        "valid": generate_email(),
        "invalid": "not-an-email",
        "empty": "",
        "long": ("a" * 256) + "@example.com",
        "xss": "<script>alert(1)</script>",
        "unknown": f"unknown_qa_{random.randint(1000, 9999)}@example.com",
    }

    password_map = {
        "valid": generate_password(valid=True),
        "invalid": generate_password(valid=False),
        "empty": "",
        "short": "aB1!",
        "xss": "<script>alert(1)</script>",
        "wrong": generate_password(valid=True),
    }

    utc = random.randint(-12, 14)
    timezone_map = {
        "valid": f"UTC{utc:+d}",
        "invalid": "UTC-16",
        "empty": "",
        "xss": "<script>alert(1)</script>",
    }

    if email_type not in email_map:
        raise ValueError(f"Unknown email type: {email_type}")
    if password_type not in password_map:
        raise ValueError(f"Unknown password type: {password_type}")
    if timezone_type not in timezone_map:
        raise ValueError(f"Unknown timezone type: {timezone_type}")

    return (
        email_map[email_type],
        password_map[password_type],
        timezone_map[timezone_type],
        expected_status,
    )

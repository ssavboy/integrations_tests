import random

from utils.fake_data_generators import generate_nickname, generate_password


def parameter_generation(
    password_type, nickname_type, timezone_type, expected_status, token=False
):
    """
    Generates a test case given an password, nicknane, timzone, status.

    Args:
    password_type (str): Password type ("valid", "invalid", "empty").
    nickname_type (str): Nickname type ("valid", "invalid", "empty").
    timezone_type (str): Timezone type ("valid", "invalid", "empty").
    expected_status (int): Expected HTTP status.

    Returns:
    tuple: (password_type, nickname_type, timezone_type, expected_status)
    """

    password_map = {
        "valid": generate_password(valid=True),
        "invalid": generate_password(valid=False),
        "empty": "",
    }

    nickname_map = {
        "valid": generate_nickname(valid=True),
        "invalid": generate_nickname(valid=False),
        "empty": "",
    }

    timezone_map = {
        "valid": f"UTC{random.randint(-12, 14):+d}",
        "invalid": "UTC-16",
        "empty": "",
    }

    if password_type not in password_map:
        raise ValueError(f"Unknown email_type: {password_type}")

    if nickname_type not in nickname_map:
        raise ValueError(f"Unknown nickname_type: {nickname_type}")

    if timezone_type not in timezone_map:
        raise ValueError(f"Unknown timezone_type: {timezone_type}")

    if token is True:
        return (
            None,
            password_map[password_type],
            nickname_map[nickname_type],
            timezone_map[timezone_type],
            expected_status,
        )

    return (
        password_map[password_type],
        nickname_map[nickname_type],
        timezone_map[timezone_type],
        expected_status,
    )

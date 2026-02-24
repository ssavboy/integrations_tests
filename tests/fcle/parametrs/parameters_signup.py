from utils.fake_data_generators import generate_email


def parameter_generation(email_type, language_type, expected_status):
    """
    Generates a test case given an email and language.

    Args:
    email_type (str): Email type ("valid", "invalid", "empty", "long", "malformed", "xss").
    language_type (str): Language type ("valid", "invalid", "empty", "null", "long", "xss").
    expected_status (int): Expected HTTP status.

    Returns:
    tuple: (email, language, expected_status)
    """

    email_map = {
        "valid": generate_email(),
        "invalid": generate_email(chars=("!#$%^&*()=}{[]|\\:;\"'<>?/")),
        "empty": "",
        "long": generate_email(range_a=250, range_b=255),
        "malformed": "test@.com",
        "xss": "<script>alert('xss')</script>",
    }

    lang_map = {
        "valid": "en",
        "empty": "",
        "invalid": "xx",
        "long": "a" * 100,
        "null": None,
        "xss": "<script>alert('xss')</script>",
    }

    if email_type not in email_map:
        raise ValueError(f"Unknown email_type: {email_type}")

    if language_type not in lang_map:
        raise ValueError(f"Unknown language_type: {language_type}")

    return (email_map[email_type], lang_map[language_type], expected_status)

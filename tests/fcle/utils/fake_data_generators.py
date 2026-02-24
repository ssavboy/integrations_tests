import random
import string

from faker import Faker
from settings import LABEL

faker = Faker()
PUNCTUATION = "~!@#$%^&*()_+|{}[]:;\"'<>,.?/-"


def generate_email(range_a=6, range_b=12, chars="._"):
    """
    Generates a random email address with the specified parameters. By default, the parameters are for valid email.

    Parameters:
        range_a (int): The minimum length of the random part of the email (default is 6)
        range_b (int): The maximum length of a random email part (default is 12)
        is chars (str): Additional allowed characters in the local part of the email (default is '._')

    Returns:
        str: The generated email address in the format:
             <prefix><random_string>@<random_domain>With default value returns valid email
    """

    # static label for search in db
    label = LABEL

    username = label + (
        "".join(
            random.choice(string.ascii_lowercase + string.digits + chars)
            for _ in range(random.randint(range_a, range_b))
        )
    )

    return f"{username}@{random.choice(['gmail.com', 'yahoo.com', 'outlook.com', 'yandex.ru'])}"


def generate_password(length=12, valid=True):
    """
    Generates a password of the specified length.

        Args:
            length (int): Password length (default is 12)
            valid (bool): If True, creates a valid password (with letters of different case,
                numbers and special characters). If False, it creates an invalid password.
                (lowercase letters only)
        Returns:
            str: Generated password
    """
    if valid:
        # Valid password: letters of different case, numbers, special characters
        characters = (
            string.ascii_lowercase
            + string.ascii_uppercase
            + string.digits
            + PUNCTUATION
        )
    else:
        # Invalid password: lowercase letters only
        characters = string.ascii_lowercase

    # Password generation
    password = "".join(random.choice(characters) for _ in range(length))

    # For a valid password, we check for all types of characters.
    if valid:
        while not (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in string.punctuation for c in password)
        ):
            password = "".join(random.choice(characters) for _ in range(length))

    return password


def generate_nickname(length=8, valid=True):
    """
    Generates a username of the specified length.

        Args:
            length (int): Username length (default 8)
            valid (bool): If True, creates a valid username (only letters,
                        numbers, underscores, minimum 3 characters). If False, creates
                        invalid user name (contains invalid characters or
                        too short)
        Returns:
            str: Generated username
    """
    if length < 3 and valid:
        length = 1  # Minimum length for a valid name

    if valid:
        # Valid name: only letters, numbers and underscores
        characters = string.ascii_lowercase + string.digits + "_"
    else:
        # Invalid name: includes invalid characters
        characters = (
            string.ascii_lowercase
            + string.digits
            + string.punctuation  # Adding invalid characters
        )

    # User name generation
    username = "".join(random.choice(characters) for _ in range(length))

    # For an invalid name, we can reduce the length to 1-2 characters.
    if not valid and random.choice([True, False]):
        username = username[: random.randint(1, 2)]

    # For a valid name, make sure that there are no spaces or other invalid characters.
    if valid:
        while (
            any(c in string.punctuation.replace("_", "") for c in username)
            or " " in username
        ):
            username = "".join(random.choice(characters) for _ in range(length))

    return username


def generate_first_name():
    """Return a random first name."""
    return faker.first_name()


def generate_last_name():
    """Return a random last name."""
    return faker.last_name()


def generate_bio():
    """Return a short fake bio / description."""
    return faker.sentence(nb_words=random.randint(5, 15))


def generate_country():
    """Return a random country name."""
    return faker.country()[:50]


def generate_city():
    """Return a random city name."""
    return faker.city()


def generate_text(length=50):
    """Return a random text with given length"""
    return faker.text(max_nb_chars=length)
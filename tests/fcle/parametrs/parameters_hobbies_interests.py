"""
    Generate lists of valid and invalid hobbie id and
    lists of valid and invalid interests id
"""

import random
from functools import lru_cache

import pytest
import requests

from settings import CONTENT_URL, ENDPOINTS

BASE_URL = f"{CONTENT_URL}{ENDPOINTS['general_categories']}"
CATEGORY_TYPES = {"hobbies": 4, "interests": 5}  # Maps category names to type IDs


def parameters_hobbies(valid=True) -> list:
    """Returns list of valid or invalid hobby IDs."""

    return parameters_by_type("hobbies", valid)


def parameters_interests(valid=True) -> list:
    """Returns list of valid or invalid interest IDs."""

    return parameters_by_type("interests", valid)


def parameters_by_type(category_type: str, valid=True) -> list:
    """
    Returns valid or invalid IDs for specified category.

    Args:
        category_type: Category type ("hobbies" or "interests")
        valid: If True returns valid IDs, else returns invalid IDs

    Returns:
        List of IDs for the specified category
    """
    return (
        valid_id_generator(category_type)
        if valid
        else invalid_id_generator(category_type)
    )


@lru_cache(maxsize=2)
def hobbies_interests_request(category_type: str) -> requests.Response:
    """
    Fetches category data from API.

    Args:
        category_type: Category type ("hobbies" or "interests")

    Returns:
        Response object with category data

    Raises:
        ValueError: If invalid category type provided
        pytest.fail: If request fails
    """

    if category_type not in CATEGORY_TYPES:
        raise ValueError(f"Unknown category type: {category_type}")

    query_params = {"typeId": CATEGORY_TYPES[category_type], "lang": "en"}

    try:
        r = requests.get(url=BASE_URL, params=query_params)

    except requests.exceptions.RequestException as e:
        pytest.fail(f"Request failed: {e}")

    return r


@lru_cache(maxsize=2)
def valid_id_generator(category_type: str) -> list:
    """Returns list of valid IDs for specified category."""

    data = hobbies_interests_request(category_type)
    list_id = []

    for d in data.json():
        list_id.append(d["id"])

    return list_id


def invalid_id_generator(category_type: str):
    """
    Generates invalid IDs not present in valid IDs.

    Args:
        category_type: Category type ("hobbies" or "interests")

    Returns:
        List of invalid IDs for the specified category
    """

    valid_id = valid_id_generator(category_type)
    invalid_id = []

    while len(invalid_id) < len(valid_id):
        rand_id = random.randint(-100, 1000)
        if rand_id not in valid_id:
            invalid_id.append(rand_id)

    return invalid_id


if __name__ == "__main__":

    print(parameters_hobbies(True))
    print(parameters_hobbies(False))

    print(parameters_interests(True))
    print(parameters_interests(False))

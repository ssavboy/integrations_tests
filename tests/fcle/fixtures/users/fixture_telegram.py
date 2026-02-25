from http import HTTPStatus

import pytest
import requests

from settings import CONFLICT, ENDPOINTS
from utils.fake_data_generators import generate_email, generate_nickname

USERS_TELEGRAM = ENDPOINTS["telegram"]

OK = HTTPStatus.OK
CREATED = HTTPStatus.CREATED
BAD_REQUEST = HTTPStatus.BAD_REQUEST
UNPROCESSABLE_ENTITY = HTTPStatus.UNPROCESSABLE_ENTITY

BASE_URL = "http://example.com/api"

TEST_USER = {
    "email": "test_api@exmaple.com",
    "password": "Test123!",
    "timezone": "Europe/Moscow",
}


class TelegramUser:
    """
    Класс для работы с API /Users/telegram.
    Инкапсулирует операции POST для разных сценариев.
    """

    endpoint = USERS_TELEGRAM

    def __init__(self, headers, post_request, payload, expected_statuses):
        self.headers = headers
        self.post_request = post_request
        self.payload = payload
        self.expected_statuses = expected_statuses

    def create(self):
        """
        Создать пользователя через POST /Users/telegram
        """
        response = self.post_request(self.payload, self.endpoint, headers=self.headers)
        return response, self.expected_statuses


@pytest.fixture(scope="session")
def auth_headers_tg():
    response = requests.post(f"{BASE_URL}/Auth/login", json=TEST_USER)
    assert response.status_code == 200, f"Auth failed: {response.text}"

    data = response.json()
    token = data.get("token") or data.get("accessToken") or data.get("jwtToken")
    assert token, f"No token found in login response: {data}"

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def telegram_cases():
    """
    Набор сценариев для тестирования Users/telegram
    """
    return {
        "valid_user": (
            {
                "telegramId": "_________",
                "username": generate_nickname(),
                "firstName": "Test",
                "lastName": "User",
                "email": generate_email(),
                "phoneNumber": "+1234567890",
                "telegramAccount": "@test_account",
            },
            [OK, CREATED],
        ),
        "minimal_data": (
            {
                "telegramId": "_________",
                "username": generate_nickname(),
                "telegramAccount": "@minimal_account",
            },
            [OK, CREATED],
        ),
        "invalid_data": (
            {"username": generate_nickname()},
            OK,
        ),
    }


@pytest.fixture
def telegram_user(auth_headers, post_request):
    """
    Фабрика для создания TelegramUser
    """

    def _make(payload, expected_statuses):
        return TelegramUser(auth_headers[0], post_request, payload, expected_statuses)

    return _make

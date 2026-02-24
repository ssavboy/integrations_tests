from http import HTTPStatus

import pytest

from fixtures.new_teacher.fixture_new_teacher import new_teacher
from fixtures.teaching_experiences.fixture_teaching_experiences import (
    create_auth_token,
    teaching_experiences,
)
from fixtures.teaching_experiences.fixture_teaching_experiences_cases import (
    _invalid_payload,
    _valid_payload,
    _validate_response_jsonschema,
)
from settings import CONFLICT

OK = HTTPStatus.OK
CREATED = HTTPStatus.CREATED

BAD_REQUEST = HTTPStatus.BAD_REQUEST
UNAUTHORIZED = HTTPStatus.UNAUTHORIZED


@pytest.mark.teaching_experiences
class TestTeachingExperiences:

    @pytest.fixture(autouse=True)
    def setup(self, create_auth_token, teaching_experiences):
        self.headers = create_auth_token
        self.client = teaching_experiences(self.headers)

    def _add_experience(
        self, payload=None
    ):  # TODO: поднять _add_experience до фикстуры, рефакторить код
        """Добавление Teacher Experience"""

        if payload == None:
            payload = _valid_payload()

        try:
            response_post = self.client.add(payload)

            return response_post.json(), response_post.status_code

        except Exception as e:
            pytest.fail(f"Ошибка: {e}")

    def test_post_unauthorized(self):
        """Тест: запрос от неавторизованного пользователя"""

        payload = _valid_payload()

        base = self.client.base
        response = self.client._post(payload, base)

        assert response.status_code == UNAUTHORIZED, (
            f"Expected 401, got {response.status_code}",
            f"{response.text}",
        )

    def test_post_valid_experience(self):
        """Тест: добавление валидного Teaching Experience"""

        payload = _valid_payload()

        response_post = self.client.add(payload)

        assert response_post.status_code in (CREATED, OK), (
            f"Request body: {payload}\n"
            f"Response: {response_post.text}\n"
            f"Status code: {response_post.status_code}"
        )

        response = self.client.get()

        assert response.status_code == OK, (
            f"Response: {response.text}\n" f"Status code: {response.status_code}"
        )

    def test_post_invalid_experience(self):
        """Тест: добавление невалидного Teaching Experience"""

        payload = _invalid_payload()

        response_post = self.client.add(payload)

        assert response_post.status_code == CONFLICT, (
            f"Request body: {payload}\n"
            f"Response: {response_post.text}\n"
            f"Status code: {response_post.status_code}"
        )

    def test_put_experience_by_id(self):
        """Тест: обновление Teacher Experience по id"""

        # Добавление Teaching Experience
        payload = _valid_payload()
        exp_data, _ = self._add_experience(payload=payload)
        exp_id = exp_data["id"]

        # Генерация нового payload и обновление experience по id
        new_payload = _valid_payload()
        response_put = self.client.put(new_payload, exp_id)

        assert response_put.status_code in (CREATED, OK), (
            f"Request body: {payload}\n"
            f"Response: {response_put.text}\n"
            f"Status code: {response_put.status_code}"
        )

        # Получение experience по id
        response = self.client.get_by_id(exp_id)

        assert response.status_code in (OK, CREATED), (
            f"Response: {response.text}\n" f"Status code: {response.status_code}"
        )

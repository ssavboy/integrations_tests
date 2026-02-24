from http import HTTPStatus

import pytest

from fixtures.new_teacher.fixture_new_teacher import new_teacher
from fixtures.teaching_experiences.fixture_teaching_experiences import (
    create_auth_token,
    teaching_experiences,
)
from fixtures.teaching_experiences.fixture_teaching_experiences_cases import (
    _valid_payload,
    _validate_response_jsonschema,
)

OK = HTTPStatus.OK

UNAUTHORIZED = HTTPStatus.UNAUTHORIZED
NOT_FOUND = HTTPStatus.NOT_FOUND
UNPROCESSABLE = HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.teaching_experiences
class TestTeachingExperiences:

    @pytest.fixture(autouse=True)
    def setup(self, create_auth_token, teaching_experiences):
        self.headers = create_auth_token
        self.client = teaching_experiences(self.headers)
        self._cleanup_experiences()

    def _cleanup_experiences(self):
        """Очистка Teacher Experiences пользователя перед тестом."""

        try:
            response = self.client.get()
            experiences = response.json()
            for exp in experiences:
                if "id" in exp:
                    self.client.delete(exp["id"])

        except Exception as e:
            pytest.fail(f"Ошибка: {e}")

    def _add_experience(self, payload=None):
        """Добавление Teacher Experience"""

        if payload == None:
            payload = _valid_payload()

        try:
            response_post = self.client.add(payload)

            return response_post.json(), response_post.status_code

        except Exception as e:
            pytest.fail(f"Ошибка: {e}")

    def test_get_unauthorized(self):
        """Тест: запрос от неавторизованного пользователя"""

        base = self.client.base
        response = self.client._get(base)

        assert response.status_code == UNAUTHORIZED, (
            f"Expected 401, got {response.status_code}",
            f"{response.text}",
        )

    def test_empty_list_for_new_user(self):
        """Тест: новый пользователь имеет пустой список опыта преподавания."""

        response = self.client.get()

        assert response.status_code == OK, f"Expected 200, got {response.status_code}"

        if response.status_code == OK:
            experiences = response.json()
            assert isinstance(
                experiences, list
            ), f"Expected list, got {type(experiences)}"
            assert experiences == [], f"Expected empty list, got {experiences}"

    def test_get_experience(self):
        """Тест: добавление валидного Teaching Experience и получение списка Experiences"""

        _, _ = self._add_experience(payload=None)

        response = self.client.get()

        if response.status_code == OK:
            experiences = response.json()
            assert (
                len(experiences) == 1
            ), f"Expected 1 Teacher Experiences, got {len(experiences)}: {experiences}"

    def test_get_experience_by_id(self):
        """Тест: получение Teacher Experience по id"""

        payload = _valid_payload()
        exp_data, _ = self._add_experience(payload=payload)
        exp_id = exp_data["id"]

        response = self.client.get_by_id(exp_id)

        assert response.status_code == OK, (
            f"Response: {response.text}\n" f"Status code: {response.status_code}"
        )

        data = response.json()
        validation_status, message = _validate_response_jsonschema(data)

        assert validation_status == True, f"{message}"

    def test_get_by_nonexistent_id(self):
        """Тест: получение Teacher Experience по несуществующему id"""

        payload = _valid_payload()
        exp_data, _ = self._add_experience(payload=payload)

        # Получаем id и увеличиваем на 1, чтобы id гарантированно не существовало
        exp_id = exp_data["id"] + 1

        response = self.client.get_by_id(exp_id)

        assert response.status_code in (NOT_FOUND, UNPROCESSABLE, HTTPStatus.GONE), (
            f"Response: {response.text}\n" f"Status code: {response.status_code}"
        )

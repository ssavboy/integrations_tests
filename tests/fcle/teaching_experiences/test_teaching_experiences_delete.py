import pytest

from http import HTTPStatus

from fixtures.teaching_experiences.fixture_teaching_experiences import teaching_experiences, create_auth_token
from fixtures.teaching_experiences.fixture_teaching_experiences_cases import _valid_payload
from fixtures.new_teacher.fixture_new_teacher import new_teacher


OK = HTTPStatus.OK
UNAUTHORIZED = HTTPStatus.UNAUTHORIZED


@pytest.mark.teaching_experiences
class TestTeachingExperiences:

    @pytest.fixture(autouse=True)
    def setup(self, create_auth_token, teaching_experiences):
        self.headers = create_auth_token
        self.client = teaching_experiences(self.headers)

    def _add_experience(self, payload=None):
        """Добавление Teacher Experience"""
        
        if payload == None:
            payload = _valid_payload()
        
        try:
            response_post = self.client.add(payload)
            
            return response_post.json(), response_post.status_code
        
        except Exception as e:
            pytest.fail(f"Ошибка: {e}")


    def test_delete_unauthorized(self):
        """Тест: запрос от неавторизованного пользователя"""

        exp_data, _ = self._add_experience()
        exp_id = exp_data["id"]

        base = self.client.base
        response = self.client._delete(None, f"{base}/{exp_id}")

        assert response.status_code == UNAUTHORIZED, (
            f"Expected 401, got {response.status_code}",
            f"{response.text}"
        )

    def test_delete_experience_by_id(self):
        """Тест: запрос от неавторизованного пользователя"""

        exp_data, _ = self._add_experience()
        exp_id = exp_data["id"]

        base = self.client.base
        response = self.client.delete(exp_id)

        assert response.status_code == OK, (
            f"Expected 200, got {response.status_code}",
            f"{response.text}"
        )

        try:
            response = self.client.get()
            experiences = response.json()
            
            assert experiences == [], \
                f"Expected empty list, got {experiences}"
        
        except Exception as e:
            pytest.fail(f"Ошибка: {e}")
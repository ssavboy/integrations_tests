import pytest

from settings import ENDPOINTS
from parametrs.parameters_new_teacher import ParametrsNewTeacher
from http import HTTPStatus
from fixtures.new_teacher.fixture_new_teacher import new_teacher


class TeachingExperiences:
    def __init__(self, headers, get_request, post_request, delete_request, put_request):
        self.headers = headers
        self._get = get_request
        self._post = post_request
        self._delete = delete_request
        self._put = put_request
        self.base = ENDPOINTS["Teaching_Experiences"]

    def get(self):
        return self._get(self.base, headers=self.headers)
    
    def get_by_id(self, exp_id: int):
        return self._get(f"{self.base}/{exp_id}", headers=self.headers)

    def add(self, payload: dict):
        return self._post(payload, self.base, headers=self.headers)

    def delete(self, exp_id: int):
        return self._delete(None, f"{self.base}/{exp_id}", headers=self.headers)

    def put(self, payload: dict, exp_id: int):
        return self._put(payload, f"{self.base}/{exp_id}", headers=self.headers)


@pytest.fixture()
def create_auth_token(new_teacher):
    """Фикстура для создания аутентификационного токена."""
    
    def _factory():
        # Генерируем валидные параметры для создания учителя
        param = ParametrsNewTeacher.parametr_generation(status=HTTPStatus.OK)
        
        # Используем переданные параметры для создания учителя
        teacher_instance = new_teacher(param)
        
        # Выполняем POST-запрос для создания учителя и получения токена
        post_response, post_expected_status = teacher_instance.post_new_teacher()
        
        # Извлекаем токен из ответа, если статус успешный
        return teacher_instance.token if post_response.status_code == HTTPStatus.OK else None
    
    return _factory


@pytest.fixture
def teaching_experiences(create_auth_token, get_request, post_request, delete_request, put_request):
    """Фикстура для создания объекта TeachingExperiences с готовым токеном."""
    
    def _factory(headers=None):
        # Получаем токен с помощью фикстуры create_auth_token
        token = create_auth_token()
        
        if token:
            # Создаем и возвращаем объект TeachingExperiences с полученным токеном
            return TeachingExperiences(token, get_request, post_request, delete_request, put_request)
    
    return _factory
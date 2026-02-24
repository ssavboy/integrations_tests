import pytest
import json
from copy import deepcopy

from settings import ENDPOINTS

TEACHER_EDU_ENDPOINT = ENDPOINTS["teacher_educations"]


class TeacherEducationsClient:
    """
    Лёгкий клиент для работы с эндпоинтом TeacherEducations.

    Обёртка вокруг фикстуры `get_request` из conftest, позволяющая удобно
    выполнять GET-запросы с нужными заголовками и query-параметрами.

    Основные возможности:
        - Автоматически подставляет `Authorization` хедер, если тестовый сценарий
          требует авторизации (requires_auth=True).
        - Добавляет стандартный Accept-заголовок ("application/json"), как в Swagger.
        - Принимает на вход любые query-параметры (filter, skip/take и т.п.).
        - Позволяет эмулировать разные сценарии: авторизованный/неавторизованный
          пользователь, битый токен, неизвестные query-параметры.

    Args:
        get_request (callable): фикстура, делающая реальный HTTP GET-запрос
                                (оборачивает requests.get).
        headers_tuple_or_dict (dict | tuple): исходные заголовки либо пара (headers, email),
                                              возвращаемая фикстурой auth_headers.
        requires_auth (bool): флаг, нужен ли токен авторизации.
        params (dict | None): query-параметры для GET-запроса.

    Methods:
        get():
            Выполняет GET-запрос к эндпоинту TeacherEducations с учётом всех настроек.
            Возвращает объект `requests.Response`.
    """

    def __init__(self, get_request, headers_tuple_or_dict, requires_auth: bool, params: dict | None):
        self._get = get_request
        self._requires_auth = requires_auth
        self._params = params or {}
        self._raw_headers = headers_tuple_or_dict

    @staticmethod
    def _unpack_headers(hdrs):
        if isinstance(hdrs, tuple) and len(hdrs) == 2 and isinstance(hdrs[0], dict):
            return deepcopy(hdrs[0])
        return deepcopy(hdrs) if isinstance(hdrs, dict) else {}

    def get(self):
        headers = {"Accept": "application/json"}
        if self._requires_auth:
            headers |= self._unpack_headers(self._raw_headers)
        return self._get(TEACHER_EDU_ENDPOINT, params=self._params, headers=headers)


@pytest.fixture
def teacher_educations(auth_headers, get_request):
    def _make(case):
        hdrs = {}
        if case.requires_auth:
            if case.label == "invalid_token":
                # подменяем на мусорный токен
                hdrs = {"Authorization": "Bearer invalid.token.value"}
            else:
                hdrs = auth_headers
        return TeacherEducationsClient(get_request, hdrs, case.requires_auth, case.params)
    return _make


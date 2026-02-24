import pytest
from copy import deepcopy
from settings import ENDPOINTS
from parametrs.parameters_teacher_educations import generate_cases

TEACHER_EDU_ENDPOINT = ENDPOINTS["teacher_educations"]


class TeacherEducationsPostClient:
    """
    Мини-клиент для POST /TeacherEducations.
    Обёртка вокруг фикстуры post_request.
    """

    def __init__(self, post_request, headers_tuple_or_dict, requires_auth: bool, payload: dict | None):
        self._post = post_request
        self._requires_auth = requires_auth
        self._payload = payload or {}
        self._raw_headers = headers_tuple_or_dict

    @staticmethod
    def _unpack_headers(hdrs):
        if isinstance(hdrs, tuple) and len(hdrs) == 2 and isinstance(hdrs[0], dict):
            return deepcopy(hdrs[0])
        return deepcopy(hdrs) if isinstance(hdrs, dict) else {}

    def post(self):
        headers = {"Accept": "application/json"}
        if self._requires_auth:
            headers |= self._unpack_headers(self._raw_headers)
        return self._post(self._payload, TEACHER_EDU_ENDPOINT, headers=headers)


@pytest.fixture(params=generate_cases("POST"), ids=lambda c: f"POST-{c.label}")
def teacher_educations_post(auth_headers, post_request, request):
    """
    Фикстура-фабрика для POST /TeacherEducations.

    Возвращает пару (client, case):
        client — объект TeacherEducationsPostClient.
        case — описание тест-кейса (TeacherEducationsCase).
    """
    case = request.param
    hdrs = {}
    if case.requires_auth:
        if case.label == "invalid_token":
            hdrs = {"Authorization": "Bearer invalid.token"}
        else:
            hdrs = auth_headers
    client = TeacherEducationsPostClient(post_request, hdrs, case.requires_auth, case.payload)
    return client, case

import pytest
from copy import deepcopy
from datetime import datetime
from settings import ENDPOINTS

BASE = ENDPOINTS["teacher_educations"]
NEW_TEACHER = ENDPOINTS.get("new_teacher", "newteacher")


class TeacherEducationByIdClient:
    def __init__(self, get_request, headers_tuple_or_dict, requires_auth: bool, id_value):
        self._get = get_request
        self._requires_auth = requires_auth
        self._id = id_value
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

        endpoint = f"{BASE}/{self._id}"
        return self._get(endpoint, headers=headers)


def _to_headers(hdrs):
    if isinstance(hdrs, tuple) and len(hdrs) == 2 and isinstance(hdrs[0], dict):
        return deepcopy(hdrs[0])
    return deepcopy(hdrs) if isinstance(hdrs, dict) else {}


@pytest.fixture
def teacher_education_by_id(auth_headers, get_request, post_request):
    """
    Для case 'ok_existing' заранее создаём учителя и одну запись образования,
    берём её id и тестируем GET по нему.
    """
    def _make(case):
        hdrs = {}
        if case.requires_auth:
            if case.label == "invalid_token":
                hdrs = {"Authorization": "Bearer invalid.token.value"}
            else:
                hdrs = auth_headers

        effective_id = case.id_value

        if case.label == "ok_existing" and case.requires_auth and case.label != "invalid_token":
            headers = _to_headers(hdrs)

            # 1) Создаём учителя — минимально валидный payload
            payload_teacher = {
                "teacherType": 1,   # обязателен
                "languageId": 1,    # обязателен (иначе 409 teacher.languageId.isRequired)
                "about": "autotest"
            }
            r_teacher = post_request(payload_teacher, NEW_TEACHER, headers=headers)
            assert r_teacher.status_code in (200, 201), f"newteacher failed: {r_teacher.status_code} {r_teacher.text}"

            # 2) Создаём запись образования
            yr = datetime.now().year
            payload_edu = {
                "institutionName": "AutoTest University",
                "degreeId": 1,
                "fieldOfStudy": "QA",
                "startYear": yr - 1,
                "finishYear": yr,
            }
            r_create = post_request(payload_edu, BASE, headers=headers)
            assert r_create.status_code in (200, 201), f"create education failed: {r_create.status_code} {r_create.text}"

            # 3) Достаём id созданной записи (подстраховка по ключам)
            try:
                created = r_create.json()
            except Exception:
                created = {}

            created_id = (
                created.get("id")
                or created.get("teacherEducationsId")
                or created.get("educationId")
            )
            assert isinstance(created_id, int) and created_id > 0, f"No id in create response: {r_create.text}"
            effective_id = created_id

        return TeacherEducationByIdClient(get_request, hdrs, case.requires_auth, effective_id)

    return _make

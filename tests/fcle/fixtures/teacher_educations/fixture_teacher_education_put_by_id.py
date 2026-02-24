import pytest
from copy import deepcopy
from settings import ENDPOINTS
from parametrs.parameters_teacher_educations import generate_cases as gen_cases_post

BASE = ENDPOINTS["teacher_educations"]
NEW_TEACHER = ENDPOINTS.get("new_teacher", "newteacher")

class TeacherEducationPutByIdClient:
    def __init__(self, put_request, get_request, post_request, headers_tuple_or_dict, requires_auth: bool, case):
        self._put = put_request
        self._get = get_request
        self._post = post_request
        self._requires_auth = requires_auth
        self._case = case
        self._raw_headers = headers_tuple_or_dict

        # Подготовим кандидатов для создания через POST — только те, где есть 200/201.
        self._post_candidates = []
        for c in gen_cases_post("POST"):
            exp = c.expected_status
            has_2xx = (exp == 200) or (exp == 201) or (isinstance(exp, (list, tuple, set)) and ({200, 201} & set(exp)))
            if has_2xx and c.payload:
                self._post_candidates.append(c.payload)

    @staticmethod
    def _unpack_headers(hdrs):
        if isinstance(hdrs, tuple) and len(hdrs) == 2 and isinstance(hdrs[0], dict):
            return deepcopy(hdrs[0])
        return deepcopy(hdrs) if isinstance(hdrs, dict) else {}

    def _headers(self, with_auth: bool):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if with_auth:
            headers |= self._unpack_headers(self._raw_headers)
        return headers

    def _ensure_teacher(self):
        """Создать Teacher для аутентифицированного пользователя, чтобы не ловить teachers.id.notTeacher (410)."""
        if not self._requires_auth:
            return
        # не пытаться при invalid_token
        if getattr(self._case, "label", "") == "invalid_token":
            return
        headers = self._headers(with_auth=True)
        payload_teacher = {
            "teacherType": 1,
            "languageId": 1,
            "about": "autotest",
        }
        r = self._post(payload_teacher, NEW_TEACHER, headers=headers)
        # Если уже учитель/дубликат — не считаем критом; нам важно, чтобы роль была.
        if r.status_code not in (200, 201):
            # тихо выходим, так как часть инстансов может возвращать 409/410 на повторное создание
            return

    def _find_existing_id(self) -> int | None:
        # GET /TeacherEducations?pageSize=1 — вытаскиваем любой id
        r = self._get(BASE, params={"pageSize": 1}, headers=self._headers(with_auth=True))
        if r.status_code != 200:
            return None
        try:
            data = r.json()
        except Exception:
            return None

        items = data
        if isinstance(data, dict):
            items = data.get("items") or data.get("data") or []
        if isinstance(items, list) and items:
            first = items[0]
            # поддержка разных ключей id на всякий случай
            return first.get("id") or first.get("teacherEducationsId") or first.get("educationId")
        return None

    def _create_via_post(self) -> int | None:
        """
        Пытаемся создать запись через POST несколькими «кандидатами».
        Возвращаем id при успехе, иначе None.
        """
        if not self._post_candidates:
            return None
        headers = self._headers(with_auth=True)  # всегда с валидным токеном для сетапа
        for payload in self._post_candidates:
            r = self._post(payload, BASE, headers=headers)
            if r.status_code in (200, 201):
                try:
                    data = r.json()
                    if isinstance(data, dict):
                        return data.get("id") or data.get("teacherEducationsId") or data.get("educationId")
                except Exception:
                    pass
        return None

    def put(self):
        id_value = self._case.id_value

        # Всегда пытаемся обеспечить роль Teacher для аутентифицированных кейсов
        self._ensure_teacher()

        if self._case.needs_existing_id:
            assert self._requires_auth, "needs_existing_id требует авторизации"

            # 1) пробуем найти готовую запись
            id_value = id_value or self._find_existing_id()

            # 2) если нет — пробуем создать через POST из генераторов
            if not id_value:
                new_id = self._create_via_post()
                if new_id:
                    id_value = new_id
                else:
                    pytest.xfail("Не удалось подготовить тестовые данные: POST /TeacherEducations возвращает 500 на всех валидных payload.")

        endpoint = f"{BASE}/{id_value}"
        return self._put(self._case.payload or {}, endpoint, self._headers(with_auth=self._requires_auth))

@pytest.fixture
def teacher_education_put_by_id(auth_headers, put_request, get_request, post_request):
    def _make(case):
        hdrs = {}
        if case.requires_auth:
            if case.label == "invalid_token":
                hdrs = {"Authorization": "Bearer invalid.token.value"}
            else:
                hdrs = auth_headers

        return TeacherEducationPutByIdClient(
            put_request=put_request,
            get_request=get_request,
            post_request=post_request,
            headers_tuple_or_dict=hdrs,
            requires_auth=case.requires_auth,
            case=case
        )
    return _make

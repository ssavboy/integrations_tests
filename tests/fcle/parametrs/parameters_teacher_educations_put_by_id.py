from dataclasses import dataclass
from typing import Iterable, Optional, Union, Dict, Any
from datetime import datetime

CUR_YEAR = datetime.now().year

@dataclass(frozen=True)
class TeacherEducationPutCase:
    label: str
    id_value: Optional[Union[int, str]]
    payload: Optional[Dict[str, Any]]
    expected_status: Union[int, Iterable[int]]
    requires_auth: bool = True
    error_code: Optional[str] = None
    error_contains: Optional[str] = None
    needs_existing_id: bool = False   # нужно ли реальное существование записи

    def matches_expected(self, status_code: int) -> bool:
        if isinstance(self.expected_status, int):
            return status_code == self.expected_status
        try:
            return status_code in set(self.expected_status)
        except TypeError:
            return False

def _valid_payload() -> Dict[str, Any]:
    return {
        "institutionName": "MIPT",
        "degreeId": 2,
        "fieldOfStudy": "Applied Math",
        "startYear": CUR_YEAR - 6,
        "finishYear": CUR_YEAR - 2,
    }

def generate_cases_put_by_id():
    p_ok = _valid_payload()

    return [
        # OK — нужен реально существующий id
        TeacherEducationPutCase("ok_update_existing", None, p_ok, 200, True, needs_existing_id=True),

        # Авторизация — существование id не важно (ответит 401/403 раньше)
        TeacherEducationPutCase("unauthorized", 1, p_ok, (401, 403), requires_auth=False),
        TeacherEducationPutCase("invalid_token", 1, p_ok, (401, 200), requires_auth=True),

        # Несуществующий id — бэк может вернуть 410 Gone
        TeacherEducationPutCase(
            "not_found", 999_999, p_ok, (404, 410, 422), True,
            error_code="teacherEducation.TeacherEducation.notFound"
        ),

        # Невалидные id в пути
        TeacherEducationPutCase("invalid_id_non_numeric", "abc", p_ok, (400, 404, 409, 422)),
        TeacherEducationPutCase("invalid_id_zero", 0, p_ok, (400, 404, 410, 422)),
        TeacherEducationPutCase("invalid_id_negative", -5, p_ok, (400, 404, 410, 422)),

        # Валидации тела — бэк шлёт 409 на конфликты/валидацию
        TeacherEducationPutCase("empty_institution", None, {**p_ok, "institutionName": ""}, (400, 409, 422), needs_existing_id=True),
        TeacherEducationPutCase("too_long_institution", None, {**p_ok, "institutionName": "A"*256}, (400, 409, 422), needs_existing_id=True),
        TeacherEducationPutCase("null_institution", None, {**p_ok, "institutionName": None}, (400, 409, 422), needs_existing_id=True),

        TeacherEducationPutCase("too_long_fieldOfStudy", None, {**p_ok, "fieldOfStudy": "A"*256}, (400, 409, 422), needs_existing_id=True),
        TeacherEducationPutCase("null_fieldOfStudy", None, {**p_ok, "fieldOfStudy": None}, (400, 409, 422), needs_existing_id=True),

        TeacherEducationPutCase("invalid_degree", None, {**p_ok, "degreeId": 10_000}, (400, 409, 422), needs_existing_id=True),

        TeacherEducationPutCase("future_startYear", None, {**p_ok, "startYear": CUR_YEAR + 1}, (400, 409, 422), needs_existing_id=True),
        TeacherEducationPutCase("finish_before_start", None, {**p_ok, "startYear": 2020, "finishYear": 2010}, (400, 409, 422), needs_existing_id=True),

        # частичный апдейт — тоже нужен существующий id
        TeacherEducationPutCase("partial_nullables", None, {
            "institutionName": "MIPT",
            "degreeId": None,
            "fieldOfStudy": None,
            "startYear": CUR_YEAR - 10,
            "finishYear": None
        }, (200, 400, 409, 422), needs_existing_id=True),
    ]

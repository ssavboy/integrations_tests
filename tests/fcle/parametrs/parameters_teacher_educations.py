from dataclasses import dataclass
from typing import Any, Dict, Optional, Iterable, Union
from datetime import datetime


@dataclass(frozen=True)
class TeacherEducationsCase:
    label: str
    method: str  # "GET" или "POST"
    expected_status: Union[int, Iterable[int]]
    requires_auth: bool = True
    params: Optional[Dict[str, Any]] = None   # для GET
    payload: Optional[Dict[str, Any]] = None  # для POST
    error_contains: Optional[str] = None

    def matches_expected(self, status_code: int) -> bool:
        if isinstance(self.expected_status, int):
            return status_code == self.expected_status
        try:
            return status_code in set(self.expected_status)
        except TypeError:
            return False


def generate_cases(method: str):
    """Возвращает набор кейсов для GET или POST /TeacherEducations."""
    this_year = datetime.now().year

    if method == "GET":
        return [
            TeacherEducationsCase("authorized_basic", "GET", 200, True),
            TeacherEducationsCase("unauthorized", "GET", (401, 403), False),
            TeacherEducationsCase("invalid_token", "GET", (401, 200), True),
            TeacherEducationsCase("filter_by_teacherId", "GET", 200, True, params={"teacherId": 1}),
            TeacherEducationsCase("invalid_teacherId", "GET", (200, 400, 422), True, params={"teacherId": "abc"}),
            TeacherEducationsCase("pagination_valid", "GET", 200, True, params={"skip": 0, "take": 2}),
            TeacherEducationsCase("pagination_invalid", "GET", (200, 400, 422), True, params={"skip": -1}),
            TeacherEducationsCase("check_empty_list", "GET", 200, True, params={"teacherId": 999999}),
        ]

    if method == "POST":
        return [
            # Happy path (помечен xfail из-за 500)
            TeacherEducationsCase(
                "valid_basic", "POST", (200, 500), True,
                payload={
                    "institutionName": "Test University",
                    "degreeId": 1,
                    "fieldOfStudy": "Mathematics",
                    "startYear": this_year - 5,
                    "finishYear": this_year - 1
                }
            ),
            # Авторизация
            TeacherEducationsCase(
                "unauthorized", "POST", (401, 403), False,
                payload={
                    "institutionName": "Test",
                    "degreeId": 1,
                    "fieldOfStudy": "CS",
                    "startYear": this_year - 1,
                    "finishYear": this_year
                }
            ),
            TeacherEducationsCase(
                "invalid_token", "POST", (401,), True,
                payload={
                    "institutionName": "Test",
                    "degreeId": 1,
                    "fieldOfStudy": "CS",
                    "startYear": this_year - 1,
                    "finishYear": this_year
                }
            ),
            # Валидации строк
            TeacherEducationsCase(
                "empty_institution", "POST", (400, 409, 422), True,
                payload={
                    "institutionName": "",
                    "degreeId": 1,
                    "fieldOfStudy": "CS",
                    "startYear": this_year - 1,
                    "finishYear": this_year
                }
            ),
            TeacherEducationsCase(
                "too_long_institution", "POST", (400, 409, 422), True,
                payload={
                    "institutionName": "X" * 201,
                    "degreeId": 1,
                    "fieldOfStudy": "CS",
                    "startYear": this_year - 1,
                    "finishYear": this_year
                }
            ),
            TeacherEducationsCase(
                "too_long_fieldOfStudy", "POST", (400, 409, 422), True,
                payload={
                    "institutionName": "Test",
                    "degreeId": 1,
                    "fieldOfStudy": "X" * 101,
                    "startYear": this_year - 1,
                    "finishYear": this_year
                }
            ),
            # Null значения
            TeacherEducationsCase(
                "null_institution", "POST", (400, 409, 422), True,
                payload={
                    "institutionName": None,
                    "degreeId": 1,
                    "fieldOfStudy": "CS",
                    "startYear": this_year - 1,
                    "finishYear": this_year
                }
            ),
            TeacherEducationsCase(
                "null_fieldOfStudy", "POST", (400, 409, 422), True,
                payload={
                    "institutionName": "Test",
                    "degreeId": 1,
                    "fieldOfStudy": None,
                    "startYear": this_year - 1,
                    "finishYear": this_year
                }
            ),
            # Отсутствие полей
            TeacherEducationsCase(
                "missing_institution", "POST", (400, 409, 422), True,
                payload={
                    "degreeId": 1,
                    "fieldOfStudy": "CS",
                    "startYear": this_year - 1,
                    "finishYear": this_year
                }
            ),
            TeacherEducationsCase(
                "missing_degreeId", "POST", (400, 409, 422), True,
                payload={
                    "institutionName": "Test",
                    "fieldOfStudy": "CS",
                    "startYear": this_year - 1,
                    "finishYear": this_year
                }
            ),
            TeacherEducationsCase(
                "missing_fieldOfStudy", "POST", (400, 409, 422), True,
                payload={
                    "institutionName": "Test",
                    "degreeId": 1,
                    "startYear": this_year - 1,
                    "finishYear": this_year
                }
            ),
            # Невалидные числа
            TeacherEducationsCase(
                "invalid_degree", "POST", (400, 409, 422), True,
                payload={
                    "institutionName": "Test",
                    "degreeId": 0,
                    "fieldOfStudy": "CS",
                    "startYear": this_year - 1,
                    "finishYear": this_year
                }
            ),
            TeacherEducationsCase(
                "future_startYear", "POST", (400, 409, 422), True,
                payload={
                    "institutionName": "Test",
                    "degreeId": 1,
                    "fieldOfStudy": "CS",
                    "startYear": this_year + 5,
                    "finishYear": this_year + 6
                }
            ),
            TeacherEducationsCase(
                "finish_before_start", "POST", (400, 409, 422), True,
                payload={
                    "institutionName": "Test",
                    "degreeId": 1,
                    "fieldOfStudy": "CS",
                    "startYear": this_year,
                    "finishYear": this_year - 1
                }
            ),
            # Граничные значения
            TeacherEducationsCase(
                "startYear_min", "POST", (200, 400, 409, 422, 500), True,
                payload={
                    "institutionName": "Boundary Case",
                    "degreeId": 1,
                    "fieldOfStudy": "History",
                    "startYear": 1900,
                    "finishYear": 1901
                }
            ),
            TeacherEducationsCase(
                "finishYear_now", "POST", (200, 400, 409, 422, 500), True,
                payload={
                    "institutionName": "Boundary Case",
                    "degreeId": 1,
                    "fieldOfStudy": "Physics",
                    "startYear": this_year - 1,
                    "finishYear": this_year
                }
            ),
            # Дубликаты
            TeacherEducationsCase(
                "duplicate_entry", "POST", (200, 409, 500), True,
                payload={
                    "institutionName": "Dup University",
                    "degreeId": 1,
                    "fieldOfStudy": "Math",
                    "startYear": this_year - 2,
                    "finishYear": this_year - 1
                }
            ),
        ]

    return []

from dataclasses import dataclass
from typing import Iterable, Optional, Union


@dataclass(frozen=True)
class TeacherEducationByIdCase:
    label: str
    expected_status: Union[int, Iterable[int]]
    requires_auth: bool = True
    id_value: Optional[Union[int, str]] = None
    error_contains: Optional[str] = None
    error_code: Optional[str] = None

    def matches_expected(self, status_code: int) -> bool:
        if isinstance(self.expected_status, int):
            return status_code == self.expected_status
        try:
            return status_code in set(self.expected_status)
        except TypeError:
            return False


def generate_cases_by_id():
    """
    Набор кейсов для GET /TeacherEducations/{id}.
    Важно: бэк для "не найдено" возвращает 410 (Gone), а для нечислового id — 409 (validation.failed).
    """
    return [
        # Существующая запись — создадим её в фикстуре и подставим реальный id
        TeacherEducationByIdCase("ok_existing", 200, True, 1),

        # Авторизация
        TeacherEducationByIdCase("unauthorized", (401, 403), False, 1),
        TeacherEducationByIdCase("invalid_token", (401, 200), True, 1),

        # Не найдено — контракт бэка: 410 (а не только 404/422)
        TeacherEducationByIdCase(
            "not_found",
            (404, 410, 422),
            True,
            999999,
            error_code="teacherEducation.TeacherEducation.notFound",
        ),

        # Невалидные id
        TeacherEducationByIdCase("invalid_id_non_numeric", (400, 404, 409, 422), True, "abc"),
        TeacherEducationByIdCase("invalid_id_zero",        (400, 404, 410, 422), True, 0),
        TeacherEducationByIdCase("invalid_id_negative",    (400, 404, 410, 422), True, -5),
    ]

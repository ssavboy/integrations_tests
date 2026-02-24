from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import pytest
from settings import ENDPOINTS

TEACHER_EDU_ENDPOINT = ENDPOINTS["teacher_educations"]
NEW_TEACHER = ENDPOINTS.get("new_teacher", "newteacher")
THIS_YEAR = datetime.now().year


# ---------- helpers / генерации ----------
def make_accept_text_plain(headers: Dict[str, str]) -> Dict[str, str]:
    """Добавляем Accept: text/plain (как в Swagger у DELETE)."""
    return {**headers, "Accept": "text/plain"}


def _ensure_teacher(post_request, headers: Dict[str, str]) -> None:
    """
    Гарантируем, что текущий пользователь имеет роль Teacher.
    Если уже есть или бэк вернул конфликт — не считаем ошибкой.
    """
    if not headers or "authorization" not in {k.lower() for k in headers.keys()}:
        return
    payload_teacher = {
        "teacherType": 1,
        "languageId": 1,
        "about": "autotest",
    }
    r = post_request(payload_teacher, NEW_TEACHER, headers=headers)
    # нам достаточно попытки; 200/201 — ок, иные коды не считаем критом для сетапа


def build_teacher_education_payload(
    institution: str = "Tmp University",
    degree_id: int = 1,   # ВАЖНО: должен существовать в БД, иначе POST может дать 500
    field: str = "QA",
    start_year: Optional[int] = None,
    finish_year: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Валидный payload под ваш валидатор:
      - InstitutionName: not null/empty, len<=200
      - DegreeId: >0
      - FieldOfStudy: not null/empty, len<=100
      - StartYear: (если задан) <= текущего года
      - FinishYear: обязателен; если есть StartYear — FinishYear >= StartYear
    """
    if start_year is None:
        start_year = THIS_YEAR - 3
    if start_year > THIS_YEAR:
        start_year = THIS_YEAR

    if finish_year is None:
        finish_year = max(start_year, THIS_YEAR - 1)

    institution = (institution or "X")[:200]
    field = (field or "X")[:100]

    return {
        "institutionName": institution,
        "degreeId": degree_id,
        "fieldOfStudy": field,
        "startYear": start_year,
        "finishYear": finish_year,
    }


def _extract_id_from_response_json(data: Any) -> Optional[int]:
    if isinstance(data, dict) and isinstance(data.get("id"), int):
        return data["id"]
    if isinstance(data, int):
        return data
    if isinstance(data, str) and data.isdigit():
        return int(data)
    if isinstance(data, list) and data and isinstance(data[0], dict) and isinstance(data[0].get("id"), int):
        return data[0]["id"]
    return None


def create_teacher_education(
    post_request,
    headers: Dict[str, str],
) -> Tuple[Optional[int], "requests.Response"]:
    """Создаёт запись через API и возвращает (id, response). Если не удалось — id=None."""
    # гарантируем роль Teacher перед созданием
    _ensure_teacher(post_request, headers=headers)

    payload = build_teacher_education_payload()
    resp = post_request(payload, TEACHER_EDU_ENDPOINT, headers=headers)
    edu_id: Optional[int] = None
    try:
        edu_id = _extract_id_from_response_json(resp.json())
    except Exception:
        pass
    return edu_id, resp


# ---------- клиент под DELETE ----------
class TeacherEducationsDeleteClient:
    def __init__(self, delete_request, headers: Dict[str, str]):
        self._delete = delete_request
        self.headers = headers

    def delete(self, edu_id: Any):
        # допускаем как int, так и str (для негативных кейсов по биндингу)
        return self._delete(None, f"{TEACHER_EDU_ENDPOINT}/{edu_id}", headers=self.headers)


# ---------- кейсы ----------
@dataclass(frozen=True)
class DeleteCase:
    label: str
    requires_auth: bool
    header_kind: str            # "valid" | "invalid" | "none"
    id_value: Any               # допускаем int/str; None => создадим запись
    expected_statuses: tuple[int, ...]
    create_before: bool = False


def generate_delete_cases() -> list[DeleteCase]:
    """
    Учтено поведение бэка:
      - notFound отдается как 410 (Gone)
      - нечисловые/слишком большие id -> 409 validation.failed
    """
    return [
        # Позитив — сначала создаём, потом удаляем
        DeleteCase("existing_ok", True, "valid", None, (200,), create_before=True),

        # Без авторизации / битый токен
        DeleteCase("unauthorized", False, "none", 999_999_999, (401, 403)),
        DeleteCase("invalid_token", True, "invalid", 999_999_999, (401, 403)),

        # Не существует / граничные id
        DeleteCase("not_found_or_false", True, "valid", 987_654_321, (200, 404, 410, 422)),
        DeleteCase("negative_id", True, "valid", -1, (200, 400, 404, 410, 422)),
        DeleteCase("zero_id", True, "valid", 0, (200, 400, 404, 410, 422)),

        # Доп. границы/форматы path-параметра
        DeleteCase("max_int32", True, "valid", 2_147_483_647, (200, 404, 410, 422)),
        DeleteCase("beyond_int32", True, "valid", 2_147_483_648, (400, 404, 409, 422)),
        DeleteCase("string_id_alpha", True, "valid", "abc", (400, 404, 409, 422)),
    ]


# ---------- фикстура, готовящая client+case+id ----------
@pytest.fixture
def client_case_delete_teacher_educations(
    request, delete_request, post_request, auth_headers
):
    """
    Возвращает (client, case, target_id):
      client — обёртка над delete_request,
      case   — текущий сценарий,
      target_id — id, по которому бьём DELETE (может быть создан заранее).
    """
    case: DeleteCase = request.param

    # headers
    if case.requires_auth:
        if case.header_kind == "invalid":
            headers = {"Authorization": "Bearer invalid.token"}
        else:
            headers, _ = auth_headers
    else:
        headers = {}
    headers = make_accept_text_plain(headers)

    # если авторизация валидна — заранее обеспечим роль Teacher (чтобы не ловить teachers.id.notTeacher)
    if case.requires_auth and case.header_kind == "valid":
        _ensure_teacher(post_request, headers=headers)

    # id
    target_id: Any = case.id_value
    if case.create_before:
        created_id, post_resp = create_teacher_education(post_request, headers=headers)
        if not created_id:
            pytest.skip(
                f"[{case.label}] Не удалось создать запись (POST нестабилен). "
                f"status={getattr(post_resp, 'status_code', '?')}, body={getattr(post_resp, 'text', '?')!r}"
            )
        target_id = created_id

    client = TeacherEducationsDeleteClient(delete_request, headers=headers)
    return client, case, target_id

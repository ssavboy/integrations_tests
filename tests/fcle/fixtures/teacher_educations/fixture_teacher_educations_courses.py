from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import pytest
from settings import ENDPOINTS

# Base endpoints
TEACHER_EDU_ENDPOINT = ENDPOINTS["teacher_educations"]
TEACHER_EDU_COURSES_ENDPOINT = f"{TEACHER_EDU_ENDPOINT}/courses"


# ---------- Data structures ----------
@dataclass(frozen=True)
class CoursesCase:
    label: str
    requires_auth: bool
    header_kind: str        # 'valid' | 'invalid' | 'none'
    accept_kind: str        # 'text' | 'json' | 'weird' | 'none' | 'any' | 'app_wild' | 'weighted'
    expected_statuses: Tuple[int, ...]


# ---------- Client ----------
class TeacherEducationsCoursesClient:
    def __init__(self, get_request, headers: Dict[str, str]):
        self._get = get_request
        self.headers = headers or {}

    def list(self, params: Optional[Dict[str, Any]] = None):
        # ВАЖНО: вызываем именованными параметрами, чтобы не перепутать порядок
        return self._get(
            endpoint=TEACHER_EDU_COURSES_ENDPOINT,
            params=params,
            headers=self.headers,
        )


# ---------- Generators ----------
def generate_courses_cases() -> List[CoursesCase]:
    """
    Базовая матрица + доп. кейсы по Accept.
    """
    cases: List[CoursesCase] = [
        CoursesCase("ok_text_plain", True,  "valid",  "text",    (200,)),
        CoursesCase("ok_json_accept", True, "valid",  "json",    (200, 406)),
        CoursesCase("unauthorized",   False, "none",  "text",    (200, 401, 403)),
        CoursesCase("invalid_token",  True, "invalid","text",    (401, 403)),
        CoursesCase("weird_accept",   True, "valid",  "weird",   (200, 406)),
        CoursesCase("no_accept",      True, "valid",  "none",    (200,)),
        # Доп. покрытие по контент-неготиэйшну
        CoursesCase("accept_any",       True, "valid", "any",       (200,)),
        CoursesCase("accept_app_wild",  True, "valid", "app_wild",  (200,)),
        CoursesCase("accept_weighted",  True, "valid", "weighted",  (200, 406)),
    ]
    return cases


def _build_headers(base_headers: Dict[str, str], case: CoursesCase) -> Dict[str, str]:
    headers = dict(base_headers or {})
    # Accept header variants
    if case.accept_kind == "text":
        headers["Accept"] = "text/plain"
    elif case.accept_kind == "json":
        headers["Accept"] = "application/json"
    elif case.accept_kind == "weird":
        headers["Accept"] = "application/xml"
    elif case.accept_kind == "any":
        headers["Accept"] = "*/*"
    elif case.accept_kind == "app_wild":
        headers["Accept"] = "application/*"
    elif case.accept_kind == "weighted":
        headers["Accept"] = "application/json;q=0.9, text/plain;q=0.8"
    elif case.accept_kind == "none":
        # без Accept — ок
        pass
    return headers


# ---------- Fixtures ----------
@pytest.fixture
def client_case_courses(get_request, auth_headers, request):
    """
    Возвращает (client, case) с корректно собранными заголовками под кейс.
    """
    case: CoursesCase = request.param

    # Базовые хедеры
    headers: Dict[str, str] = {}

    # Авторизация
    if case.header_kind == "none":
        headers = {}
    elif case.header_kind == "invalid":
        headers["Authorization"] = "Bearer invalid.token"
    else:
        # valid
        valid_headers, _email = auth_headers
        headers = dict(valid_headers)

    # Accept
    headers = _build_headers(headers, case)

    client = TeacherEducationsCoursesClient(get_request, headers=headers)
    return client, case


# ---------- Loose validation for single item ----------
def validate_course_item(item: Any, idx: int = 0) -> List[str]:
    """
    Мягкая проверка элемента ответа: базовая структура и типы.
    Возвращает список ошибок; пустой список — всё ок.
    """
    errs: List[str] = []
    if not isinstance(item, dict):
        errs.append(f"[{idx}] item must be object/dict, got {type(item)}")
        return errs

    keys = set(item.keys())
    has_id = any(k in keys for k in ("id", "Id", "ID", "courseId", "CourseId"))
    has_name = any(k in keys for k in ("name", "Name", "title", "Title"))
    if not has_id and not has_name:
        errs.append(f"[{idx}] expected at least 'id' or 'name'/'title' in {keys}")

    for id_key in ("id", "Id", "ID", "courseId", "CourseId"):
        if id_key in item and not isinstance(item[id_key], (int, str)):
            errs.append(f"[{idx}] `{id_key}` must be int or str, got {type(item[id_key])}")
    for nm_key in ("name", "Name", "title", "Title"):
        if nm_key in item and not isinstance(item[nm_key], str):
            errs.append(f"[{idx}] `{nm_key}` must be str, got {type(item[nm_key])}")

    return errs

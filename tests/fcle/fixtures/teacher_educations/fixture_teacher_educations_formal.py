from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import pytest
from settings import ENDPOINTS

TEACHER_EDU_ENDPOINT = ENDPOINTS["teacher_educations"]
TEACHER_EDU_FORMAL_ENDPOINT = f"{TEACHER_EDU_ENDPOINT}/formal"


# ---------- Data ----------
@dataclass(frozen=True)
class FormalCase:
    label: str
    requires_auth: bool
    header_kind: str        # 'valid' | 'invalid' | 'none'
    accept_kind: str        # 'text' | 'json' | 'weird' | 'none' | 'any' | 'app_wild' | 'weighted'
    expected_statuses: Tuple[int, ...]


# ---------- Client ----------
class TeacherEducationsFormalClient:
    def __init__(self, get_request, headers: Dict[str, str]):
        self._get = get_request
        self.headers = headers or {}

    def list(self, params: Optional[Dict[str, Any]] = None):
        return self._get(
            endpoint=TEACHER_EDU_FORMAL_ENDPOINT,
            params=params,
            headers=self.headers,
        )


# ---------- Cases ----------
def generate_formal_cases() -> List[FormalCase]:
    return [
        FormalCase("ok_text_plain",   True,  "valid",   "text",     (200,)),
        FormalCase("ok_json_accept",  True,  "valid",   "json",     (200, 406)),
        # ЗАКРЫВАЕМ ДЫРКУ: без токена 200 быть не должно
        FormalCase("unauthorized",    False, "none",    "text",     (401, 403)),
        FormalCase("invalid_token",   True,  "invalid", "text",     (401, 403)),
        FormalCase("weird_accept",    True,  "valid",   "weird",    (200, 406)),
        FormalCase("no_accept",       True,  "valid",   "none",     (200,)),
        # Доп. покрытие по Accept
        FormalCase("accept_any",      True,  "valid",   "any",      (200,)),
        FormalCase("accept_app_wild", True,  "valid",   "app_wild", (200,)),
        FormalCase("accept_weighted", True,  "valid",   "weighted", (200, 406)),
    ]


def _apply_accept(headers: Dict[str, str], kind: str) -> Dict[str, str]:
    h = dict(headers or {})
    if kind == "text":
        h["Accept"] = "text/plain"
    elif kind == "json":
        h["Accept"] = "application/json"
    elif kind == "weird":
        h["Accept"] = "application/xml"
    elif kind == "any":
        h["Accept"] = "*/*"
    elif kind == "app_wild":
        h["Accept"] = "application/*"
    elif kind == "weighted":
        h["Accept"] = "application/json;q=0.9, text/plain;q=0.8"
    # kind == "none" -> без Accept
    return h


# ---------- Fixture ----------
@pytest.fixture
def client_case_formal(get_request, auth_headers, request):
    case: FormalCase = request.param

    # auth headers
    if case.header_kind == "none":
        headers: Dict[str, str] = {}
    elif case.header_kind == "invalid":
        headers = {"Authorization": "Bearer invalid.token"}
    else:
        valid_headers, _ = auth_headers
        headers = dict(valid_headers)

    headers = _apply_accept(headers, case.accept_kind)

    client = TeacherEducationsFormalClient(get_request, headers=headers)
    return client, case


# ---------- Validation ----------
def validate_formal_item(item: Any, idx: int = 0) -> List[str]:
    """
    Мягкая валидация структуры formal-образований + вложенных documents[].
    """
    errs: List[str] = []
    if not isinstance(item, dict):
        return [f"[{idx}] item must be object/dict, got {type(item)}"]

    # верхний уровень (проверяем типы, если поля присутствуют)
    for k, t in [
        ("id", (int, str)),
        ("teacherId", (int, str)),
        ("institutionName", str),
        ("degreeId", (int, str)),
        ("fieldOfStudy", str),
        ("startYear", (int, str, type(None))),
        ("finishYear", (int, str, type(None))),
        ("createdAt", str),
        ("updatedAt", str),
    ]:
        if k in item and not isinstance(item[k], t):
            errs.append(f"[{idx}] `{k}` type mismatch: {type(item[k])} vs {t}")

    # documents[]
    docs = item.get("documents", [])
    if docs is not None:
        if not isinstance(docs, list):
            errs.append(f"[{idx}] `documents` must be list, got {type(docs)}")
        else:
            for j, d in enumerate(docs):
                if not isinstance(d, dict):
                    errs.append(f"[{idx}].documents[{j}] must be object, got {type(d)}")
                    continue
                for k, t in [
                    ("id", (int, str)),
                    ("teacherId", (int, str)),
                    ("documentType", (int, str)),
                    ("fileName", str),
                    ("fileUrl", str),
                    ("title", str),
                    ("description", str),
                ]:
                    if k in d and not isinstance(d[k], t):
                        errs.append(f"[{idx}].documents[{j}].{k} type mismatch: {type(d[k])} vs {t}")
    return errs

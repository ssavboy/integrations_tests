from __future__ import annotations

import pytest
from http import HTTPStatus
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from settings import ENDPOINTS

BASE = ENDPOINTS["accounting_terminate_package"]

OK = (HTTPStatus.OK,)
ERR_AUTH = (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)
BAD_ALL = (HTTPStatus.BAD_REQUEST, HTTPStatus.CONFLICT, HTTPStatus.UNPROCESSABLE_ENTITY)  # 400/409/422
NEGOTIATE_200_406 = (HTTPStatus.OK, HTTPStatus.NOT_ACCEPTABLE)


# ---------- кейс ----------
@dataclass(frozen=True)
class TerminateCase:
    label: str
    id_value: Any
    requires_auth: bool = True
    header_kind: str = "valid"          # 'valid' | 'invalid' | 'none'
    accept_kind: str = "text"           # 'text' | 'json' | 'xml' | 'any' | 'none' | 'text_charset' | 'json_charset'
    expected_statuses: Tuple[int, ...] = OK
    error_code_contains: Optional[str] = None

    # xfail для известных багов бэка
    xfail_on: Optional[Tuple[int, ...]] = None
    xfail_reason: Optional[str] = None


# ---------- заголовки ----------
def _apply_accept(headers: Dict[str, str], kind: str) -> Dict[str, str]:
    h = dict(headers or {})
    if kind == "text":
        h["Accept"] = "text/plain"
    elif kind == "json":
        h["Accept"] = "application/json"
    elif kind == "xml":
        h["Accept"] = "application/xml"
    elif kind == "any":
        h["Accept"] = "*/*"
    elif kind == "none":
        h.pop("Accept", None)
    elif kind == "text_charset":
        h["Accept"] = "text/plain; charset=utf-8"
    elif kind == "json_charset":
        h["Accept"] = "application/json; charset=utf-8"
    return h


def _build_headers(base_headers: Dict[str, str], case: TerminateCase) -> Dict[str, str]:
    headers = dict(base_headers or {})
    # auth
    if case.header_kind == "none":
        headers = {}
    elif case.header_kind == "invalid":
        headers["Authorization"] = "Bearer invalid.token"
    # accept
    headers = _apply_accept(headers, case.accept_kind)
    return headers


# ---------- клиент ----------
class TerminateClient:
    def __init__(self, delete_request, headers: Dict[str, str]):
        self._delete = delete_request
        self.headers = headers

    def terminate(self, id_value: Any):
        urls = [f"{BASE}/{id_value}", f"{BASE}/{id_value}/"]
        last = None
        for url in urls:
            r = self._delete(payload=None, endpoint=url, headers=self.headers)
            if r.status_code not in (HTTPStatus.NOT_FOUND, HTTPStatus.METHOD_NOT_ALLOWED):
                return r
            last = r
        return last


# ---------- мягкая валидация объекта пакета (допускаем null) ----------
def validate_package_object(obj: Any) -> List[str]:
    errs: List[str] = []
    if not isinstance(obj, dict):
        return [f"object must be dict, got {type(obj)}"]

    def ok_str(v): return v is None or isinstance(v, str)
    def ok_id(v):  return v is None or isinstance(v, (int, str))
    def ok_num(v): return v is None or isinstance(v, (int, float, str))

    # верхний уровень
    for k in ("id", "studentId", "teacherId", "packageDefId", "lessonDuration", "lessonsRemaining"):
        if k in obj and not ok_id(obj.get(k)):
            errs.append(f"`{k}` must be int/str or null")

    for k in ("title", "description", "status", "currencyCode", "createdAt", "updatedAt"):
        if k in obj and not ok_str(obj.get(k)):
            errs.append(f"`{k}` must be str or null")

    for k in ("price", "platformFee"):
        if k in obj and not ok_num(obj.get(k)):
            errs.append(f"`{k}` must be number/str or null")

    # teacher
    t = obj.get("teacher")
    if isinstance(t, dict):
        if not ok_id(t.get("id")):
            errs.append("teacher.id must be int/str or null")
        for s in ("nickname", "avatarUrl", "profilePicture"):
            if s in t and not ok_str(t.get(s)):
                errs.append(f"teacher.{s} must be str or null")
        lang = t.get("language")
        if isinstance(lang, dict):
            for s in ("languageName", "languageOwnerName", "shortName2", "shortName3"):
                if s in lang and not ok_str(lang.get(s)):
                    errs.append(f"teacher.language.{s} must be str or null")

    return errs


# ---------- кейсы ----------
def generate_cases() -> list[TerminateCase]:
    BUG500 = (HTTPStatus.INTERNAL_SERVER_ERROR,)
    BUG_REASON = "Backend bug: 500 on terminate-package (Original transaction/account mismatch not mapped to 4xx)"

    return [
        # happy/404 — сейчас бэк даёт 500 → xfail
        TerminateCase("ok_text_id_1", 1,
                      expected_statuses=(HTTPStatus.OK, HTTPStatus.NOT_FOUND, HTTPStatus.GONE),
                      xfail_on=BUG500, xfail_reason=BUG_REASON),

        # content negotiation — тоже утыкаются в 500 → xfail
        TerminateCase("accept_json", 1, accept_kind="json",
                      expected_statuses=(HTTPStatus.OK, HTTPStatus.NOT_ACCEPTABLE, HTTPStatus.NOT_FOUND, HTTPStatus.GONE),
                      xfail_on=BUG500, xfail_reason=BUG_REASON),
        TerminateCase("accept_json_charset", 1, accept_kind="json_charset",
                      expected_statuses=(HTTPStatus.OK, HTTPStatus.NOT_ACCEPTABLE, HTTPStatus.NOT_FOUND, HTTPStatus.GONE),
                      xfail_on=BUG500, xfail_reason=BUG_REASON),
        TerminateCase("accept_xml", 1, accept_kind="xml",
                      expected_statuses=(HTTPStatus.OK, HTTPStatus.NOT_ACCEPTABLE, HTTPStatus.NOT_FOUND, HTTPStatus.GONE),
                      xfail_on=BUG500, xfail_reason=BUG_REASON),
        TerminateCase("accept_any", 1, accept_kind="any",
                      expected_statuses=(HTTPStatus.OK, HTTPStatus.NOT_FOUND, HTTPStatus.GONE, HTTPStatus.GONE),
                      xfail_on=BUG500, xfail_reason=BUG_REASON),
        TerminateCase("accept_text_charset", 1, accept_kind="text_charset",
                      expected_statuses=(HTTPStatus.OK, HTTPStatus.NOT_FOUND, HTTPStatus.GONE),
                      xfail_on=BUG500, xfail_reason=BUG_REASON),
        TerminateCase("no_accept", 1, accept_kind="none",
                      expected_statuses=(HTTPStatus.OK, HTTPStatus.NOT_FOUND, HTTPStatus.GONE),
                      xfail_on=BUG500, xfail_reason=BUG_REASON),

        # авторизация — работают (оставляем без xfail)
        TerminateCase("unauthorized", 1, requires_auth=False, header_kind="none",
                      expected_statuses=ERR_AUTH),
        TerminateCase("invalid_token", 1, requires_auth=True, header_kind="invalid",
                      expected_statuses=ERR_AUTH),

        # валидация id — эти проходят, xfail не нужен
        TerminateCase("id_zero", 0, expected_statuses=(*BAD_ALL, HTTPStatus.NOT_FOUND, HTTPStatus.GONE)),
        TerminateCase("id_negative", -1, expected_statuses=(*BAD_ALL, HTTPStatus.NOT_FOUND, HTTPStatus.GONE)),
        # строка-число — сейчас тоже 500 → xfail
        TerminateCase("id_string_numeric", "1",
                      expected_statuses=(HTTPStatus.OK, HTTPStatus.NOT_FOUND, *BAD_ALL, HTTPStatus.GONE),
                      xfail_on=BUG500, xfail_reason=BUG_REASON),
        TerminateCase("id_non_numeric", "1x",
                      expected_statuses=(HTTPStatus.NOT_FOUND, *BAD_ALL),
                      error_code_contains="validation"),
        TerminateCase("id_huge", 2_147_483_648,
                      expected_statuses=(HTTPStatus.NOT_FOUND, *BAD_ALL)),

        # бизнес-конфликт — сейчас 500 → xfail
        TerminateCase("already_terminated", 1,
                      expected_statuses=(HTTPStatus.OK, HTTPStatus.CONFLICT, HTTPStatus.UNPROCESSABLE_ENTITY, HTTPStatus.GONE),
                      xfail_on=BUG500, xfail_reason=BUG_REASON),
    ]


# ---------- фикстура ----------
@pytest.fixture(params=generate_cases(), ids=lambda c: c.label)
def tp_client_case(delete_request, auth_headers, request):
    case: TerminateCase = request.param
    base_headers: Dict[str, str] = {}
    if case.requires_auth and case.header_kind == "valid":
        base_headers, _ = auth_headers
    headers = _build_headers(base_headers, case)
    client = TerminateClient(delete_request, headers=headers)
    return client, case

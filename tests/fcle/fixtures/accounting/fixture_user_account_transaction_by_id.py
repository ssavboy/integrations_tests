from __future__ import annotations

import pytest
from http import HTTPStatus
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from settings import ENDPOINTS

BASE_ENDPOINT = ENDPOINTS["accounting_user_account_transactions"]

OK = (HTTPStatus.OK,)
ERR_AUTH = (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)
BAD_ALL = (HTTPStatus.BAD_REQUEST, HTTPStatus.CONFLICT, HTTPStatus.UNPROCESSABLE_ENTITY)  # 400/409/422


# ---------- кейс ----------
@dataclass(frozen=True)
class UATByIdCase:
    label: str
    id_value: Any

    requires_auth: bool = True
    header_kind: str = "valid"       # 'valid' | 'invalid' | 'none'
    accept_kind: str = "text"        # 'text' | 'json' | 'xml' | 'any' | 'none' | 'text_charset' | 'json_charset'
    expected_statuses: Tuple[int, ...] = OK
    error_code_contains: Optional[str] = None


# ---------- helper: заголовки ----------
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


def _build_headers(base_headers: Dict[str, str], case: UATByIdCase) -> Dict[str, str]:
    headers = dict(base_headers or {})
    # auth
    if case.header_kind == "none":
        headers = {}
    elif case.header_kind == "invalid":
        headers["Authorization"] = "Bearer invalid.token"
    # accept
    headers = _apply_accept(headers, case.accept_kind)
    return headers


# ---------- client ----------
class UATByIdClient:
    def __init__(self, get_request, headers: Dict[str, str]):
        self._get = get_request
        self.headers = headers

    def get(self, id_value: Any):
        urls = [f"{BASE_ENDPOINT}/{id_value}", f"{BASE_ENDPOINT}/{id_value}/"]
        last = None
        for url in urls:
            r = self._get(endpoint=url, params=None, headers=self.headers)
            if r.status_code not in (HTTPStatus.NOT_FOUND, HTTPStatus.METHOD_NOT_ALLOWED):
                return r
            last = r
        return last


# ---------- «мягкая» проверка одного объекта (допускаем null) ----------
def validate_tx_object(obj: Any) -> List[str]:
    errs: List[str] = []
    if not isinstance(obj, dict):
        return [f"object must be dict, got {type(obj)}"]

    def ok_str(v): return v is None or isinstance(v, str)
    def ok_id(v):  return v is None or isinstance(v, (int, str))
    def ok_num(v): return v is None or isinstance(v, (int, float, str))

    # примитивы верхнего уровня
    if not ok_id(obj.get("id")):
        errs.append("`id` must be int/str or null")

    for k in ("referenceNumber", "description", "transactionDate",
              "currencyCode", "transactionType", "createdAt", "updatedAt"):
        if not ok_str(obj.get(k)):
            errs.append(f"`{k}` must be str or null")

    for k in ("totalAmount", "amount", "fee"):
        if not ok_num(obj.get(k)):
            errs.append(f"`{k}` must be number/str or null")

    for k in ("relatedAccountId", "userId", "userDepositId",
              "userWithdrawalId", "lessonId"):
        if not ok_id(obj.get(k)):
            errs.append(f"`{k}` must be int/str or null")

    # lessonPackage
    lp = obj.get("lessonPackage")
    if isinstance(lp, dict):
        if not ok_id(lp.get("id")):
            errs.append("lessonPackage.id must be int/str or null")
        if not ok_num(lp.get("price")):
            errs.append("lessonPackage.price must be number/str or null")
        for s in ("title", "description", "currencyCode", "createdAt", "updatedAt"):
            if not ok_str(lp.get(s)):
                errs.append(f"lessonPackage.{s} must be str or null")

    return errs


# ---------- кейсы ----------
def generate_cases() -> list[UATByIdCase]:
    return [
        # happy: id=1 (если транзакции нет — допустим 404)
        UATByIdCase("ok_text_plain_id_1", 1, expected_statuses=(HTTPStatus.OK, HTTPStatus.NOT_FOUND)),
        # content negotiation
        UATByIdCase("accept_json", 1, accept_kind="json",
                    expected_statuses=(HTTPStatus.OK, HTTPStatus.NOT_ACCEPTABLE, HTTPStatus.NOT_FOUND)),
        UATByIdCase("accept_json_charset", 1, accept_kind="json_charset",
                    expected_statuses=(HTTPStatus.OK, HTTPStatus.NOT_ACCEPTABLE, HTTPStatus.NOT_FOUND)),
        UATByIdCase("accept_xml", 1, accept_kind="xml",
                    expected_statuses=(HTTPStatus.OK, HTTPStatus.NOT_ACCEPTABLE, HTTPStatus.NOT_FOUND)),
        UATByIdCase("accept_any", 1, accept_kind="any",
                    expected_statuses=(HTTPStatus.OK, HTTPStatus.NOT_FOUND)),
        UATByIdCase("accept_text_charset", 1, accept_kind="text_charset",
                    expected_statuses=(HTTPStatus.OK, HTTPStatus.NOT_FOUND)),

        # авторизация
        UATByIdCase("unauthorized", 1, requires_auth=False, header_kind="none", expected_statuses=ERR_AUTH),
        UATByIdCase("invalid_token", 1, requires_auth=True, header_kind="invalid", expected_statuses=ERR_AUTH),

        # валидация id
        UATByIdCase("id_zero", 0, expected_statuses=(*BAD_ALL, HTTPStatus.NOT_FOUND, HTTPStatus.GONE)),
        UATByIdCase("id_negative", -1, expected_statuses=(*BAD_ALL, HTTPStatus.NOT_FOUND, HTTPStatus.GONE)),
        UATByIdCase("id_string_numeric", "1", expected_statuses=(HTTPStatus.OK, HTTPStatus.NOT_FOUND, *BAD_ALL, HTTPStatus.GONE)),
        UATByIdCase("id_non_numeric", "1x", expected_statuses=(HTTPStatus.NOT_FOUND, *BAD_ALL), error_code_contains="validation"),
        UATByIdCase("id_huge", 2_147_483_648, expected_statuses=(HTTPStatus.NOT_FOUND, *BAD_ALL)),
    ]


# ---------- фикстуры ----------
@pytest.fixture(params=generate_cases(), ids=lambda c: c.label)
def uat_by_id_client_case(get_request, auth_headers, request):
    case: UATByIdCase = request.param
    base_headers = {}
    if case.requires_auth and case.header_kind == "valid":
        base_headers, _ = auth_headers
    headers = _build_headers(base_headers, case)
    client = UATByIdClient(get_request, headers=headers)
    return client, case

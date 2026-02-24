from __future__ import annotations

import pytest
from http import HTTPStatus
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from settings import ENDPOINTS

ENDPOINT = ENDPOINTS["accounting_user_account_balance"]

OK = (HTTPStatus.OK,)
ERR_AUTH = (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)
NEGOTIATE_200_406 = (HTTPStatus.OK, HTTPStatus.NOT_ACCEPTABLE)


# ---------- кейс ----------
@dataclass(frozen=True)
class UABCase:
    label: str
    requires_auth: bool = True
    header_kind: str = "valid"          # 'valid' | 'invalid' | 'none'
    accept_kind: str = "text"           # 'text' | 'json' | 'xml' | 'any' | 'none' | 'text_charset' | 'json_charset'
    expected_statuses: Tuple[int, ...] = OK


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


def _build_headers(base_headers: Dict[str, str], case: UABCase) -> Dict[str, str]:
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
class UABClient:
    def __init__(self, get_request, headers: Dict[str, str]):
        self._get = get_request
        self.headers = headers

    def get_balance(self):
        # именованные параметры совместимы с твоей сигнатурой get_request(endpoint, params=None, headers=None)
        return self._get(endpoint=ENDPOINT, params=None, headers=self.headers)


# ---------- «мягкая» проверка объекта баланса ----------
def validate_balance_object(obj: Any) -> List[str]:
    errs: List[str] = []
    if not isinstance(obj, dict):
        return [f"object must be dict, got {type(obj)}"]

    # balance обязателен, но допускаем число/строку-число
    if "balance" not in obj:
        errs.append("missing `balance` field")
    else:
        val = obj["balance"]
        if not isinstance(val, (int, float, str)):
            errs.append("`balance` must be number/str")

    # если сервер присылает currencyCode — валидируем мягко
    if "currencyCode" in obj:
        cc = obj["currencyCode"]
        if not isinstance(cc, str) or len(cc) != 3 or not cc.isupper():
            errs.append("`currencyCode` must be 3 upper letters")
    return errs


# ---------- кейсы ----------
def generate_cases() -> List[UABCase]:
    return [
        # happy по Swagger: text/plain
        UABCase("ok_text_plain", True, "valid", "text", expected_statuses=(HTTPStatus.OK,)),

        # content negotiation
        UABCase("accept_json",            True, "valid", "json",         expected_statuses=NEGOTIATE_200_406),
        UABCase("accept_json_charset",    True, "valid", "json_charset", expected_statuses=NEGOTIATE_200_406),
        UABCase("accept_xml",             True, "valid", "xml",          expected_statuses=NEGOTIATE_200_406),
        UABCase("accept_any",             True, "valid", "any",          expected_statuses=(HTTPStatus.OK,)),
        UABCase("no_accept",              True, "valid", "none",         expected_statuses=(HTTPStatus.OK,)),
        UABCase("accept_text_charset",    True, "valid", "text_charset", expected_statuses=(HTTPStatus.OK,)),

        # auth
        UABCase("unauthorized",           False, "none",   "text", expected_statuses=ERR_AUTH),
        UABCase("invalid_token",          True,  "invalid","text", expected_statuses=ERR_AUTH),
    ]


# ---------- фикстуры ----------
@pytest.fixture(params=generate_cases(), ids=lambda c: c.label)
def uab_client_case(get_request, auth_headers, request):
    case: UABCase = request.param
    base_headers = {}
    if case.requires_auth and case.header_kind == "valid":
        base_headers, _ = auth_headers
    headers = _build_headers(base_headers, case)
    client = UABClient(get_request, headers=headers)
    return client, case

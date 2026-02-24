from __future__ import annotations

import pytest
from http import HTTPStatus
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from settings import ENDPOINTS

ENDPOINT = ENDPOINTS["accounting_user_account_transactions"]

OK = (HTTPStatus.OK,)
ERR_AUTH = (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)
NEGOTIATE_200_406 = (HTTPStatus.OK, HTTPStatus.NOT_ACCEPTABLE)

# ---------- кейс ----------
@dataclass(frozen=True)
class UATCase:
    label: str
    requires_auth: bool = True
    header_kind: str = "valid"     # 'valid' | 'invalid' | 'none'
    accept_kind: str = "text"      # 'text' | 'json' | 'xml' | 'any' | 'none' | 'text_charset' | 'json_charset'
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

def _build_headers(base_headers: Dict[str, str], case: UATCase) -> Dict[str, str]:
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
class UATClient:
    def __init__(self, get_request, headers: Dict[str, str]):
        self._get = get_request
        self.headers = headers

    def list(self):
        # именованные параметры важны: сигнатура get_request(endpoint, params=None, headers=None)
        return self._get(endpoint=ENDPOINT, params=None, headers=self.headers)

# ---------- валидатор одного элемента (мягкий) ----------
def validate_tx_item(item: Any, idx: int = 0) -> List[str]:
    errs: List[str] = []
    if not isinstance(item, dict):
        return [f"[{idx}] item must be object/dict, got {type(item)}"]

    # базовые поля верхнего уровня (типовая «мягкая» проверка)
    for k in ("transactionId", "accountId", "debit", "credit", "createdAt", "currencyCode"):
        if k in item:
            if k in ("transactionId", "accountId") and not isinstance(item[k], (int, str)):
                errs.append(f"[{idx}] `{k}` must be int/str, got {type(item[k])}")
            if k in ("debit", "credit") and not isinstance(item[k], (int, float, str)):
                errs.append(f"[{idx}] `{k}` must be number/str, got {type(item[k])}")
            if k in ("createdAt", "currencyCode") and not isinstance(item[k], str):
                errs.append(f"[{idx}] `{k}` must be str, got {type(item[k])}")

    acc = item.get("account")
    if isinstance(acc, dict):
        if "id" in acc and not isinstance(acc["id"], (int, str)):
            errs.append(f"[{idx}] account.id must be int/str")
        if "currencyCode" in acc and not isinstance(acc["currencyCode"], str):
            errs.append(f"[{idx}] account.currencyCode must be str")

    trx = item.get("transaction")
    if isinstance(trx, dict):
        if "id" in trx and not isinstance(trx["id"], (int, str)):
            errs.append(f"[{idx}] transaction.id must be int/str")
        for num in ("amount", "feeAmount", "totalAmount"):
            if num in trx and not isinstance(trx[num], (int, float, str)):
                errs.append(f"[{idx}] transaction.{num} must be number/str")
        for s in ("currency", "status", "transactionDate", "description"):
            if s in trx and not isinstance(s and trx[s], str):
                errs.append(f"[{idx}] transaction.{s} must be str")
    return errs

# ---------- кейсы ----------
def generate_cases() -> List[UATCase]:
    return [
        # happy: text/plain по Swagger
        UATCase("ok_text_plain", requires_auth=True, header_kind="valid", accept_kind="text", expected_statuses=(200,)),
        # content negotiation
        UATCase("accept_json",            True, "valid", "json",         expected_statuses=NEGOTIATE_200_406),
        UATCase("accept_json_charset",    True, "valid", "json_charset", expected_statuses=NEGOTIATE_200_406),
        UATCase("accept_xml",             True, "valid", "xml",          expected_statuses=NEGOTIATE_200_406),
        UATCase("accept_any",             True, "valid", "any",          expected_statuses=(200,)),
        UATCase("accept_text_charset",    True, "valid", "text_charset", expected_statuses=(200,)),
        UATCase("no_accept",              True, "valid", "none",         expected_statuses=(200,)),
        # auth
        UATCase("unauthorized",           False, "none",  "text",        expected_statuses=ERR_AUTH),
        UATCase("invalid_token",          True,  "invalid","text",       expected_statuses=ERR_AUTH),
    ]

# ---------- фикстуры ----------
@pytest.fixture(params=generate_cases(), ids=lambda c: c.label)
def uat_client_case(get_request, auth_headers, request):
    case: UATCase = request.param
    base_headers = {}
    if case.requires_auth and case.header_kind == "valid":
        base_headers, _ = auth_headers
    headers = _build_headers(base_headers, case)
    client = UATClient(get_request, headers=headers)
    return client, case

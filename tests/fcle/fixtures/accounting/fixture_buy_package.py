from __future__ import annotations

import pytest
from http import HTTPStatus
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, Iterable

from utils.http_utils import request_post, request_options, normalize_headers, variants
from settings import ENDPOINTS

# По Swagger успешный медиа-тип контролируется Accept=text/plain,
# но тело фактически JSON. Делаем гибко как в deposit.
OK = (HTTPStatus.OK, HTTPStatus.CREATED)
BAD = (HTTPStatus.BAD_REQUEST, HTTPStatus.CONFLICT, HTTPStatus.UNPROCESSABLE_ENTITY,HTTPStatus.GONE)  # 400/409/422


# ---------- Модель кейса ----------
@dataclass(frozen=True)
class BuyPackageCase:
    label: str

    # payload
    lesson_package_definition_id: Any = None  # кладём как есть, чтобы проверить биндинг

    # протокол/заголовки
    requires_auth: bool = True
    header_kind: str = "valid"      # 'valid' | 'invalid' | 'none'
    accept_kind: str = "text"       # 'text' | 'json' | 'any' | 'xml'
    content_type: str = "json"      # 'json' | 'text_plain'

    # ожидания
    expected_statuses: Tuple[int, ...] = OK
    error_contains: Optional[str] = None
    error_code_contains: Optional[str] = None

    # известные баги (xfail)
    xfail_on: Optional[Tuple[int, ...]] = None
    xfail_reason: Optional[str] = None

    def to_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if self.lesson_package_definition_id is not None:
            payload["lessonPackageDefinitionId"] = self.lesson_package_definition_id
        return payload


# ---------- Заголовки ----------
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
    return h

def _apply_content_type(headers: Dict[str, str], kind: str) -> Dict[str, str]:
    h = dict(headers or {})
    if kind == "json":
        h["Content-Type"] = "application/json"
    elif kind == "text_plain":
        h["Content-Type"] = "text/plain"   # намеренно "ломаем" для 415/400
    return h


# ---------- Клиент ----------
class BuyPackageClient:
    endpoint = ENDPOINTS.get("accounting_buy_package") or f"{ENDPOINTS.get('accounting', 'Accounting')}/buy-package"

    def __init__(self, auth_headers, case: BuyPackageCase):
        self.case = case
        self.history: list[tuple[str, str, int, str]] = []
        self.allow_map: Dict[str, str] = {}

        # auth
        headers: Dict[str, str] = {}
        if case.requires_auth:
            if case.header_kind == "invalid":
                headers["Authorization"] = "Bearer invalid.token"
            else:
                headers = normalize_headers(auth_headers)

        # accept/content-type
        headers = _apply_accept(headers, case.accept_kind)
        headers = _apply_content_type(headers, case.content_type)

        self.headers = headers

    def buy(self):
        payload = self.case.to_payload()

        # OPTIONS — лог
        for url in variants(self.endpoint):
            r = request_options(url, headers=self.headers)
            self.allow_map[url] = r.headers.get("Allow", "")
            self.history.append(("OPTIONS", url, r.status_code, self.allow_map[url]))

        # POST — пробуем без/со слэшем
        last = None
        for url in variants(self.endpoint):
            r = request_post(url, payload, headers=self.headers)
            self.history.append(("POST", url, r.status_code, getattr(r, "text", "")))
            if r.status_code not in (HTTPStatus.NOT_FOUND, HTTPStatus.METHOD_NOT_ALLOWED):
                return r
            last = r
        return last


# ---------- Кейсы ----------
def generate_cases() -> list[BuyPackageCase]:
    cases: list[BuyPackageCase] = [
        # ==== Happy (id 1, но если нет такого — допустим not-found/422 от бэка) ====
        BuyPackageCase(
            "ok_text_accept_id_1",
            1,
            expected_statuses=(HTTPStatus.OK, HTTPStatus.NOT_FOUND, HTTPStatus.UNPROCESSABLE_ENTITY, HTTPStatus.CONFLICT, HTTPStatus.GONE),
            accept_kind="text",
        ),

        # ==== Авторизация ====
        BuyPackageCase("unauthorized", 1, requires_auth=False, header_kind="none",
                       expected_statuses=(HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)),
        BuyPackageCase("invalid_token", 1, requires_auth=True, header_kind="invalid",
                       expected_statuses=(HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)),

        # ==== Валидация id ====
        BuyPackageCase("missing_id", None, expected_statuses=BAD, error_contains="lessonPackageDefinitionId"),
        BuyPackageCase("id_zero", 0, expected_statuses=BAD),
        BuyPackageCase("id_negative", -1, expected_statuses=BAD),
        # строка-число — binder часто конвертит -> допускаем 200/4xx
        BuyPackageCase("id_string_numeric", "1", expected_statuses=(HTTPStatus.OK, *BAD)),
        # реально нечисловое — у нас часто 409 validation.failed
        BuyPackageCase("id_non_numeric", "1x", expected_statuses=BAD, error_code_contains="validation.failed"),
        # большой id
        BuyPackageCase("id_huge", 2_147_483_648, expected_statuses=(HTTPStatus.BAD_REQUEST, HTTPStatus.NOT_FOUND, HTTPStatus.UNPROCESSABLE_ENTITY, HTTPStatus.CONFLICT)),

        # ==== Content Negotiation ====
        # В окружении с пустым балансом покупка падает в 422 insufficientFunds — допускаем это.
        BuyPackageCase(
            "accept_json",
            1,
            accept_kind="json",
            expected_statuses=(HTTPStatus.OK, HTTPStatus.NOT_ACCEPTABLE, HTTPStatus.UNPROCESSABLE_ENTITY, HTTPStatus.GONE),
            error_code_contains="accounting.user.insufficientFunds",
        ),
        BuyPackageCase(
            "accept_any",
            1,
            accept_kind="any",
            expected_statuses=(HTTPStatus.OK, HTTPStatus.UNPROCESSABLE_ENTITY, HTTPStatus.GONE),
            error_code_contains="accounting.user.insufficientFunds",
        ),
        BuyPackageCase(
            "no_accept_text_default",
            1,
            accept_kind="text",
            expected_statuses=(HTTPStatus.OK, HTTPStatus.UNPROCESSABLE_ENTITY, HTTPStatus.GONE),
            error_code_contains="accounting.user.insufficientFunds",
        ),

        # ==== Заголовок тела ====
        BuyPackageCase("content_type_text_plain", 1, content_type="text_plain",
                       expected_statuses=(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, HTTPStatus.BAD_REQUEST)),
    ]
    return cases


# ---------- Фикстуры ----------
@pytest.fixture
def buy_package_client(auth_headers):
    def _make(case: BuyPackageCase):
        hdrs = auth_headers if case.requires_auth and case.header_kind == "valid" else {}
        return BuyPackageClient(hdrs, case)
    return _make

@pytest.fixture(params=generate_cases(), ids=lambda c: c.label)
def buy_package_case(request):
    return request.param

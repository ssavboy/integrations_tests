import pytest
from http import HTTPStatus
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, Iterable

from utils.http_utils import request_post, request_options, normalize_headers, variants
from settings import ENDPOINTS

OK = (HTTPStatus.OK, HTTPStatus.CREATED)
# включаем 409, т.к. бэкенд мапит часть валидаций/конвертаций в Conflict
BAD = (HTTPStatus.BAD_REQUEST, HTTPStatus.CONFLICT, HTTPStatus.UNPROCESSABLE_ENTITY)  # 400,409,422


# -----------------------------------------------------
# Модель кейса
# -----------------------------------------------------
@dataclass(frozen=True)
class DepositCase:
    label: str
    # payload fields
    amount: Any = None
    fee: Any = None
    description: Optional[str] = None

    # протокол/заголовки/авторизация
    requires_auth: bool = True
    header_kind: str = "valid"      # 'valid' | 'invalid' | 'none'
    accept_kind: str = "json"       # 'json' | 'text' | 'xml' | 'any'
    content_type: str = "json"      # 'json' | 'text_plain'

    # ожидания
    expected_status: int | Tuple[int, ...] = HTTPStatus.OK
    error_contains: Optional[str] = None
    error_code_contains: Optional[str] = None

    # пометки для известных багов бэка
    xfail_on: Optional[Tuple[int, ...]] = None
    xfail_reason: Optional[str] = None

    def to_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if self.amount is not None:
            payload["amount"] = self.amount
        if self.fee is not None:
            payload["fee"] = self.fee
        if self.description is not None:
            payload["description"] = self.description
        return payload

    def matches_expected(self, status_code: int) -> bool:
        if isinstance(self.expected_status, Iterable) and not isinstance(self.expected_status, (str, bytes)):
            return status_code in set(self.expected_status)
        return status_code == self.expected_status


# -----------------------------------------------------
# Генератор кейсов
# -----------------------------------------------------
def generate_cases() -> list[DepositCase]:
    cases: list[DepositCase] = [
        # ==== Happy paths ====
        DepositCase("ok_minimal", amount=100, description="test", expected_status=OK),
        DepositCase("ok_with_fee", amount=1000, fee=25, description="with fee", expected_status=OK),

        # ==== Авторизация ====
        DepositCase(
            "unauthorized",
            amount=100,
            requires_auth=False,
            header_kind="none",
            expected_status=(HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN),
        ),
        DepositCase(
            "invalid_token",
            amount=100,
            requires_auth=True,
            header_kind="invalid",
            expected_status=(HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN),
        ),

        # ==== amount ====
        DepositCase(
            "bad_negative_amount",
            amount=-50,
            expected_status=BAD,
            error_contains="amount",
            error_code_contains="lessZero",
        ),
        DepositCase(
            "bad_missing_amount",
            amount=None,  # поле не попадёт в payload
            expected_status=BAD,
            error_contains="amount",
        ),
        DepositCase(
            "amount_zero",
            amount=0,
            expected_status=BAD,
            error_contains="amount",
        ),
        # реально НЕчисловое значение -> у бэка 409 validation.failed
        DepositCase(
            "amount_non_numeric",
            amount="100x",
            expected_status=BAD,  # (400, 409, 422)
            error_code_contains="validation.failed",
        ),
        DepositCase(
            "amount_decimal3",
            amount=100.001,
            expected_status=(HTTPStatus.OK, HTTPStatus.BAD_REQUEST, HTTPStatus.UNPROCESSABLE_ENTITY),
        ),
        # очень большое число — у бэка сейчас 500 (баг), помечаем xfail при 500
        DepositCase(
            "amount_huge",
            amount=10**12,
            expected_status=(HTTPStatus.OK, HTTPStatus.BAD_REQUEST, HTTPStatus.UNPROCESSABLE_ENTITY),
            xfail_on=(HTTPStatus.INTERNAL_SERVER_ERROR,),
            xfail_reason="Backend bug: 500 on huge amount (DB save error)",
        ),

        # ==== fee ====
        # отрицательный fee -> 409 (конфликт)
        DepositCase(
            "fee_negative",
            amount=200,
            fee=-5,
            expected_status=BAD,
            error_contains="fee",
        ),
        # НЕчисловое fee -> 409 validation.failed
        DepositCase(
            "fee_non_numeric",
            amount=200,
            fee="10x",
            expected_status=BAD,  # (400, 409, 422)
            error_code_contains="validation.failed",
        ),
        # отсутствие fee — допускается/валится в зависимости от правил
        DepositCase(
            "fee_missing",
            amount=200,
            fee=None,
            expected_status=(HTTPStatus.OK, HTTPStatus.BAD_REQUEST, HTTPStatus.UNPROCESSABLE_ENTITY),
        ),

        # ==== description ====
        # длинное описание — у бэка 409 (tooLong)
        DepositCase(
            "desc_long",
            amount=200,
            description="A" * 600,
            expected_status=BAD,
        ),
        DepositCase(
            "desc_html",
            amount=200,
            description="<script>alert(1)</script>",
            expected_status=(HTTPStatus.OK, HTTPStatus.BAD_REQUEST, HTTPStatus.UNPROCESSABLE_ENTITY),
        ),

        # ==== Content negotiation ====
        DepositCase(
            "accept_xml",
            amount=200,
            accept_kind="xml",
            expected_status=(HTTPStatus.OK, HTTPStatus.NOT_ACCEPTABLE),
        ),
        DepositCase(
            "accept_any",
            amount=200,
            accept_kind="any",
            expected_status=OK,
        ),
        DepositCase(
            "accept_text_plain",
            amount=200,
            accept_kind="text",
            expected_status=OK,
        ),

        # ==== Заголовки тела ====
        DepositCase(
            "content_type_text_plain",
            amount=200,
            content_type="text_plain",
            expected_status=(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, HTTPStatus.BAD_REQUEST),
        ),
    ]
    return cases


# -----------------------------------------------------
# Вспомогалки для заголовков
# -----------------------------------------------------
def _apply_accept(headers: Dict[str, str], kind: str) -> Dict[str, str]:
    h = dict(headers or {})
    if kind == "json":
        h["Accept"] = "application/json"
    elif kind == "text":
        h["Accept"] = "text/plain"
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
        # намеренно ломаем тип содержимого (тело всё равно будет JSON через requests)
        h["Content-Type"] = "text/plain"
    return h


# -----------------------------------------------------
# Клиент
# -----------------------------------------------------
class DepositClient:
    endpoint = ENDPOINTS.get("accounting_deposit") or f"{ENDPOINTS.get('accounting', 'Accounting')}/deposit"

    def __init__(self, auth_headers, case: DepositCase):
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

        # accept / content-type
        headers = _apply_accept(headers, case.accept_kind)
        headers = _apply_content_type(headers, case.content_type)

        self.headers = headers

    def deposit(self):
        payload = self.case.to_payload()

        # OPTIONS — логируем поддержку методов
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


# -----------------------------------------------------
# Фикстуры
# -----------------------------------------------------
@pytest.fixture
def deposit_client(auth_headers):
    """Создаёт клиента для POST /Accounting/deposit с auth/headers от кейса."""
    def _make(case: DepositCase):
        hdrs = auth_headers if case.requires_auth and case.header_kind == "valid" else {}
        return DepositClient(hdrs, case)
    return _make


@pytest.fixture(params=generate_cases(), ids=lambda c: c.label)
def deposit_case(request):
    return request.param

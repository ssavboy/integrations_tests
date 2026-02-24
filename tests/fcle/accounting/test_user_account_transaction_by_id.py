import json
import re
from decimal import Decimal, InvalidOperation
from http import HTTPStatus

import pytest

from fixtures.accounting.fixture_user_account_transaction_by_id import (
    uat_by_id_client_case,
    validate_tx_object,
)

OK = (HTTPStatus.OK,)

ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$")

# список статусов-ошибок (без 404, его добавим отдельно)
ERR_STATUSES = (
    HTTPStatus.BAD_REQUEST,
    HTTPStatus.CONFLICT,
    HTTPStatus.UNPROCESSABLE_ENTITY,
    HTTPStatus.UNAUTHORIZED,
    HTTPStatus.FORBIDDEN,
    HTTPStatus.NOT_ACCEPTABLE,
)


def _to_dec(x):
    if isinstance(x, (int, float)):
        return Decimal(str(x))
    if isinstance(x, str) and x.strip() != "":
        try:
            return Decimal(x)
        except InvalidOperation:
            return None
    return None


@pytest.mark.accounting
@pytest.mark.user_account_transaction_by_id
@pytest.mark.xfail(reason="transactionDate not ISO-8601 this issue not in priority")
def test_user_account_transaction_by_id(uat_by_id_client_case):
    client, case = uat_by_id_client_case
    r = client.get(case.id_value)

    assert r.status_code in case.expected_statuses, (
        f"[{case.label}] ожидали {case.expected_statuses}, получили {r.status_code}. "
        f"Headers={client.headers!r} Body={getattr(r,'text','')!r}"
    )

    if r.status_code in OK:
        # content-type может быть text/plain, но тело — JSON-объект
        try:
            data = r.json()
        except Exception:
            try:
                data = json.loads(r.text or "{}")
            except Exception:
                pytest.fail(f"[{case.label}] Ожидали JSON-объект. Тело={r.text!r}")

        assert isinstance(data, dict), f"[{case.label}] тело не dict: {type(data)}"

        # «мягкая» схема
        errs = validate_tx_object(data)
        assert not errs, f"[{case.label}] schema issues: {errs}"

        # Доп. инварианты: ISO-8601, валюта, суммы
        for key in ("transactionDate", "createdAt", "updatedAt"):
            if isinstance(data.get(key), str):
                assert ISO_RE.match(
                    data[key]
                ), f"[{case.label}] {key} not ISO-8601: {data[key]!r}"

        if isinstance(data.get("currencyCode"), str):
            cc = data["currencyCode"]
            assert (
                len(cc) == 3 and cc.isupper()
            ), f"[{case.label}] currencyCode must be 3 upper letters: {cc!r}"

        # totalAmount ≈ amount + fee (если все три есть)
        t = _to_dec(data.get("totalAmount"))
        a = _to_dec(data.get("amount"))
        f = _to_dec(data.get("fee"))
        if t is not None and a is not None and f is not None:
            assert abs(t - (a + f)) <= Decimal(
                "0.01"
            ), f"[{case.label}] totalAmount != amount+fee (±0.01): {t} vs {a}+{f}"
        return

    # Ошибки: иногда JSON, иногда текст — если JSON, мягко проверим error.code
    if r.status_code in (HTTPStatus.NOT_FOUND, *ERR_STATUSES):
        ctype = (r.headers.get("Content-Type") or "").lower()
        if "json" in ctype or (r.text or "").startswith("{"):
            try:
                body = r.json()
            except Exception:
                try:
                    body = json.loads(r.text)
                except Exception:
                    body = None
            if isinstance(body, dict) and case.error_code_contains:
                code = (body.get("error") or {}).get("code") or body.get("code")
                if code:
                    assert (
                        case.error_code_contains in code
                    ), f"[{case.label}] ожидали code содержащий '{case.error_code_contains}', получили {code!r}"
        else:
            assert isinstance(r.text, str)

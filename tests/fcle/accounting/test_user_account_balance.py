import pytest
from http import HTTPStatus
import json
from decimal import Decimal, InvalidOperation

from fixtures.accounting.fixture_user_account_balance import (
    uab_client_case,
    validate_balance_object,
)

OK = (HTTPStatus.OK,)

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
@pytest.mark.user_account_balance
def test_user_account_balance(uab_client_case):
    client, case = uab_client_case
    r = client.get_balance()

    assert r.status_code in case.expected_statuses, (
        f"[{case.label}] ожидали {case.expected_statuses}, получили {r.status_code}. "
        f"Headers={client.headers!r} Body={getattr(r,'text','')!r}"
    )

    if r.status_code in OK:
        # content-type часто text/plain, но тело — JSON
        try:
            data = r.json()
        except Exception:
            try:
                data = json.loads(r.text or "{}")
            except Exception:
                pytest.fail(f"[{case.label}] Ожидали JSON-объект. Тело={r.text!r}")

        assert isinstance(data, dict), f"[{case.label}] тело не dict: {type(data)}"

        errs = validate_balance_object(data)
        assert not errs, f"[{case.label}] schema issues: {errs}"

        # баланс должен быть приводим к Decimal
        bal = _to_dec(data.get("balance"))
        assert bal is not None, f"[{case.label}] balance is not a number/str-number: {data.get('balance')!r}"

        # если вдруг приходит currencyCode — проверим его на всякий случай (валидатор уже проверил формат)
        if "currencyCode" in data:
            assert isinstance(data["currencyCode"], str)


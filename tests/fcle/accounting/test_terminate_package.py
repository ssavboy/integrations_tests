import pytest
from http import HTTPStatus
import json, re
from decimal import Decimal, InvalidOperation

from fixtures.accounting.fixture_terminate_package import tp_client_case, validate_package_object

OK = (HTTPStatus.OK,)
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$")

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
@pytest.mark.terminate_package
def test_terminate_package(tp_client_case):
    client, case = tp_client_case
    r = client.terminate(case.id_value)

    # Хук для известных багов бэка (см. xfail_on/xfail_reason в кейсах)
    if getattr(case, "xfail_on", None) and r.status_code in case.xfail_on:
        pytest.xfail(getattr(case, "xfail_reason", f"Backend bug on {r.status_code}"))

    assert r.status_code in case.expected_statuses, (
        f"[{case.label}] ожидали {case.expected_statuses}, получили {r.status_code}. "
        f"Headers={client.headers!r} Body={getattr(r,'text','')!r}"
    )

    # ---- успех ----
    if r.status_code in OK:
        # text/plain, но тело — JSON-объект
        try:
            data = r.json()
        except Exception:
            try:
                data = json.loads(r.text or "{}")
            except Exception:
                pytest.fail(f"[{case.label}] Ожидали JSON-объект. Тело={r.text!r}")

        assert isinstance(data, dict), f"[{case.label}] тело не dict: {type(data)}"

        errs = validate_package_object(data)
        assert not errs, f"[{case.label}] schema issues: {errs}"

        # мягкие инварианты
        if isinstance(data.get("createdAt"), str):
            assert ISO_RE.match(data["createdAt"]), f"[{case.label}] createdAt not ISO-8601: {data['createdAt']!r}"
        if isinstance(data.get("updatedAt"), str):
            assert ISO_RE.match(data["updatedAt"]), f"[{case.label}] updatedAt not ISO-8601: {data['updatedAt']!r}"
        if isinstance(data.get("currencyCode"), str):
            cc = data["currencyCode"]
            assert len(cc) == 3 and cc.isupper(), f"[{case.label}] currencyCode must be 3 upper letters: {cc!r}"
        if "lessonsRemaining" in data:
            lr = _to_dec(data.get("lessonsRemaining"))
            if lr is not None:
                assert lr >= 0, f"[{case.label}] lessonsRemaining < 0: {lr}"
        if "price" in data:
            assert _to_dec(data["price"]) is not None, f"[{case.label}] price not numeric-like: {data['price']!r}"
        return

    # ---- ошибки/валидации ----
    if r.status_code in (
        HTTPStatus.BAD_REQUEST, HTTPStatus.CONFLICT, HTTPStatus.UNPROCESSABLE_ENTITY,
        HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN,
        HTTPStatus.NOT_ACCEPTABLE, HTTPStatus.NOT_FOUND
    ):
        ctype = (r.headers.get("Content-Type") or "").lower()
        body = None
        if "json" in ctype or (r.text or "").startswith("{"):
            try:
                body = r.json()
            except Exception:
                try:
                    body = json.loads(r.text)
                except Exception:
                    body = None
        if isinstance(body, dict) and getattr(case, "error_code_contains", None):
            code = (body.get("error") or {}).get("code") or body.get("code")
            if code:
                assert case.error_code_contains in code, (
                    f"[{case.label}] ожидали code содержащий '{case.error_code_contains}', получили {code!r}"
                )
        else:
            assert isinstance(r.text, str)

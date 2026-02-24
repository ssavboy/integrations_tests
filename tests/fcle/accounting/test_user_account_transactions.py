import pytest
from http import HTTPStatus
import json, re
from decimal import Decimal, InvalidOperation

from fixtures.accounting.fixture_user_account_transactions import uat_client_case, validate_tx_item

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
@pytest.mark.user_account_transactions
def test_user_account_transactions(uat_client_case):
    client, case = uat_client_case
    r = client.list()

    assert r.status_code in case.expected_statuses, (
        f"[{case.label}] ожидали {case.expected_statuses}, получили {r.status_code}. "
        f"Headers={client.headers!r} Body={getattr(r,'text','')!r}"
    )

    if r.status_code in OK:
        # content-type может быть text/plain, тело — JSON-массив
        try:
            data = r.json()
        except Exception:
            try:
                data = json.loads(r.text or "[]")
            except Exception:
                pytest.fail(f"[{case.label}] Ожидали JSON-массив. Тело={r.text!r}")

        assert isinstance(data, list), f"[{case.label}] ожидали список, а не {type(data)}"
        if not data:
            return

        # базовая «мягкая» схема
        for idx, item in enumerate(data[:50]):
            errs = validate_tx_item(item, idx)
            assert not errs, f"[{case.label}] schema issues: {errs}"

        # доп. инварианты
        seen_ids = set()
        for idx, item in enumerate(data[:50]):
            # ISO-8601 даты
            created_at = item.get("createdAt")
            if isinstance(created_at, str):
                assert ISO_RE.match(created_at), f"[{idx}] createdAt not ISO-8601: {created_at!r}"

            trx = item.get("transaction") or {}
            trx_dt = trx.get("transactionDate")
            if isinstance(trx_dt, str):
                assert ISO_RE.match(trx_dt), f"[{idx}] transaction.transactionDate not ISO-8601: {trx_dt!r}"

            # Валюта
            cc = item.get("currencyCode")
            if isinstance(cc, str):
                assert len(cc) == 3 and cc.isupper(), f"[{idx}] currencyCode must be 3 upper letters: {cc!r}"
            trx_cc = trx.get("currency")
            if isinstance(trx_cc, str):
                assert len(trx_cc) == 3 and trx_cc.isupper(), f"[{idx}] transaction.currency must be 3 upper letters: {trx_cc!r}"

            # Суммы: debit/credit >= 0 и не оба > 0
            d = _to_dec(item.get("debit"))
            c = _to_dec(item.get("credit"))
            if d is not None:
                assert d >= 0, f"[{idx}] debit < 0: {d}"
            if c is not None:
                assert c >= 0, f"[{idx}] credit < 0: {c}"
            if d is not None and c is not None:
                assert not (d > 0 and c > 0), f"[{idx}] both debit and credit > 0: d={d} c={c}"

            # Согласованность с transaction.amount (±0.01)
            t_amount = _to_dec(trx.get("amount"))
            if t_amount is not None and (d is not None or c is not None):
                if d is not None and d > 0:
                    assert abs(t_amount - d) <= Decimal("0.01"), f"[{idx}] amount != debit (±0.01): {t_amount} vs {d}"
                elif c is not None and c > 0:
                    assert abs(t_amount - c) <= Decimal("0.01"), f"[{idx}] amount != credit (±0.01): {t_amount} vs {c}"

            # Уникальность transactionId (первые 50)
            tid = item.get("transactionId")
            if tid is not None:
                key = str(tid)
                assert key not in seen_ids, f"[{idx}] duplicate transactionId={tid}"
                seen_ids.add(key)

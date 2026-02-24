import pytest
import json
from http import HTTPStatus
from fixtures.accounting.fixture_deposit import deposit_client, deposit_case

OK_STATUSES = (HTTPStatus.OK, HTTPStatus.CREATED)

@pytest.mark.accounting
@pytest.mark.deposit
def test_deposit(deposit_client, deposit_case):
    client = deposit_client(deposit_case)
    response = client.deposit()

    # если маршрут реально не разрешает POST — пропускаем (сервер не готов)
    if response.status_code == HTTPStatus.METHOD_NOT_ALLOWED:
        pytest.skip(f"POST не разрешён. Allow={client.allow_map}. История={client.history}")

    # Известные баги бэка помечаем xfail (например, 500 на огромном amount)
    if getattr(deposit_case, "xfail_on", None) and response.status_code in deposit_case.xfail_on:
        pytest.xfail(getattr(deposit_case, "xfail_reason", f"Known backend bug on {response.status_code}"))

    # Универсальная проверка по ожиданиям кейса
    assert deposit_case.matches_expected(response.status_code), (
        f"{deposit_case.label}: ожидали {deposit_case.expected_status}, "
        f"получили {response.status_code}. История={client.history}"
    )

    # ---- Успех ----
    if response.status_code in OK_STATUSES:
        try:
            data = response.json()
        except Exception:
            pytest.fail(f"{deposit_case.label}: Ожидали JSON в ответе. Тело={response.text!r}")

        assert isinstance(data, dict), f"{deposit_case.label}: JSON-объект ожидался, got {type(data)}"
        if isinstance(deposit_case.amount, (int, float)):
            assert "amount" in data, f"{deposit_case.label}: нет поля 'amount' в ответе {data}"
            assert data["amount"] == pytest.approx(deposit_case.amount), (
                f"{deposit_case.label}: ожидали amount={deposit_case.amount}, получили {data['amount']}"
            )
        if deposit_case.fee is not None and isinstance(deposit_case.fee, (int, float)):
            if "feeAmount" in data:
                assert data["feeAmount"] == pytest.approx(deposit_case.fee)
        return

    # ---- Ошибки/валидации ----
    if response.status_code in (
        HTTPStatus.BAD_REQUEST, HTTPStatus.CONFLICT, HTTPStatus.UNPROCESSABLE_ENTITY,
        HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN,
        HTTPStatus.NOT_ACCEPTABLE, HTTPStatus.UNSUPPORTED_MEDIA_TYPE
    ):
        ctype = (response.headers.get("Content-Type") or "").lower()
        if "json" in ctype:
            try:
                body = response.json()
            except json.JSONDecodeError:
                pytest.fail(f"{deposit_case.label}: ожидали JSON в ошибке; raw={response.text!r}")

            assert isinstance(body, dict), f"{deposit_case.label}: тело ошибки не dict: {type(body)}"
            if deposit_case.error_contains:
                assert deposit_case.error_contains.lower() in (response.text or "").lower(), (
                    f"{deposit_case.label}: не нашли '{deposit_case.error_contains}' в ответе: {response.text!r}"
                )
            if deposit_case.error_code_contains:
                code = None
                if "error" in body and isinstance(body["error"], dict):
                    code = body["error"].get("code")
                code = code or body.get("code")
                if code:
                    assert deposit_case.error_code_contains in code, (
                        f"{deposit_case.label}: ожидали code, содержащий '{deposit_case.error_code_contains}', получили {code!r}"
                    )
        else:
            assert isinstance(response.text, str)

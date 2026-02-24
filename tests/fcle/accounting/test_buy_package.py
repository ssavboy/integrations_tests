import pytest
import json
from http import HTTPStatus

from fixtures.accounting.fixture_buy_package import buy_package_client, buy_package_case

OK = (HTTPStatus.OK, HTTPStatus.CREATED)

@pytest.mark.accounting
@pytest.mark.buy_package
def test_buy_package(buy_package_client, buy_package_case):
    client = buy_package_client(buy_package_case)
    r = client.buy()

    if r.status_code == HTTPStatus.METHOD_NOT_ALLOWED:
        pytest.skip(f"POST не разрешён. Allow={client.allow_map}. История={client.history}")

    # xfail для известных багов (если появятся)
    if getattr(buy_package_case, "xfail_on", None) and r.status_code in buy_package_case.xfail_on:
        pytest.xfail(getattr(buy_package_case, "xfail_reason", f"Known backend bug on {r.status_code}"))

    assert r.status_code in buy_package_case.expected_statuses, (
        f"[{buy_package_case.label}] ожидали {buy_package_case.expected_statuses}, получили {r.status_code}. "
        f"История={client.history}"
    )

    # ---- 200 OK ----
    if r.status_code in OK:
        # content-type может быть text/plain, но тело — JSON
        try:
            data = r.json()
        except Exception:
            pytest.fail(f"[{buy_package_case.label}] Ожидали JSON в ответе. Тело={r.text!r}")

        assert isinstance(data, dict), f"[{buy_package_case.label}] тело не dict: {type(data)}"

        # мягкая схема: проверяем только базовые типы, если ключи присутствуют
        if "id" in data:
            assert isinstance(data["id"], (int, str))
        for key in ("title", "description", "status", "currencyCode"):
            if key in data:
                assert isinstance(data[key], str)
        for key in ("price", "platformFee"):
            if key in data:
                assert isinstance(data[key], (int, float, str))  # иногда сервер шлёт строки для денег
        if "createdAt" in data:
            assert isinstance(data["createdAt"], str)
        if "updatedAt" in data:
            assert isinstance(data["updatedAt"], str)
        if "teacher" in data and isinstance(data["teacher"], dict):
            if "id" in data["teacher"]:
                assert isinstance(data["teacher"]["id"], (int, str))
        if "user" in data and isinstance(data["user"], dict):
            if "id" in data["user"]:
                assert isinstance(data["user"]["id"], (int, str))
        return

    # ---- Ошибки / валидация ----
    if r.status_code in (
        HTTPStatus.BAD_REQUEST, HTTPStatus.CONFLICT, HTTPStatus.UNPROCESSABLE_ENTITY,
        HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN,
        HTTPStatus.NOT_ACCEPTABLE, HTTPStatus.UNSUPPORTED_MEDIA_TYPE, HTTPStatus.NOT_FOUND
    ):
        ctype = (r.headers.get("Content-Type") or "").lower()
        if "json" in ctype or r.text.startswith("{"):
            try:
                body = r.json()
            except json.JSONDecodeError:
                pytest.fail(f"[{buy_package_case.label}] ожидали JSON-ошибку; raw={r.text!r}")

            assert isinstance(body, dict)

            # “мягкая” проверка problem-json или error-json
            if buy_package_case.error_contains:
                assert buy_package_case.error_contains.lower() in (r.text or "").lower(), \
                    f"[{buy_package_case.label}] не нашли '{buy_package_case.error_contains}' в ответе: {r.text!r}"
            if buy_package_case.error_code_contains:
                code = (body.get("error") or {}).get("code") or body.get("code")
                if code:
                    assert buy_package_case.error_code_contains in code, \
                        f"[{buy_package_case.label}] ожидали code содержащий '{buy_package_case.error_code_contains}', получили {code!r}"
        else:
            # допускаем text/plain / пустое тело
            assert isinstance(r.text, str)

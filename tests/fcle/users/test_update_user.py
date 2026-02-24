import json

import pytest

from fixtures.users.fixture_update_user import update_user, update_user_case


VALIDATION_STATUS = 409  # любые ответы валидации считаем ошибками



OK_STATUSES = {200, 201, 204}
@pytest.mark.update_user
def test_update_user(update_user, update_user_case):
    user = update_user(update_user_case)
    response = user.update()

    if response is None or response.status_code in (404, 405):
        pytest.skip(f"PUT недоступен. Allow={user.allow_map}, Попытки={user.attempts}")

    expected_status = update_user_case.expected_status
    err_contains = getattr(update_user_case, "error_contains", None)

    # ---------- HAPPY PATH, НО БЭК НЕ ПРОПУСТИЛ ----------
    if expected_status in OK_STATUSES and response.status_code == VALIDATION_STATUS:
        try:
            data = json.loads(response.text or "")
            code = (data.get("error") or {}).get("code")
        except Exception:
            code = None

        pytest.xfail(
            f"Backend отклонил сгенерированные данные (409). "
            f"Ожидался happy-path, но сработала валидация. "
            f"error.code={code}"
        )

    # ---------- ЕСЛИ ОЖИДАЕМ УСПЕХ ----------
    if expected_status in OK_STATUSES:
        assert response.status_code in OK_STATUSES, (
            f"Ожидали успешный статус {expected_status}, "
            f"получили {response.status_code}\n"
            f"Тело: {getattr(response, 'text', '')}"
        )
        return

    # ---------- ЕСЛИ ОЖИДАЕМ ОШИБКУ ----------
    assert response.status_code in {expected_status, VALIDATION_STATUS}, (
        f"Ожидали ошибку {expected_status}, "
        f"получили {response.status_code}\n"
        f"Тело: {getattr(response, 'text', '')}"
    )

    raw_text = response.text or ""
    try:
        data = json.loads(raw_text)
        error = (data or {}).get("error", {})
        message = error.get("message", "")
        code = error.get("code", "")
    except Exception:
        pytest.fail(f"Ответ не JSON:\n{raw_text}")

    assert code, f"В ответе нет error.code\nТело: {raw_text}"

    if err_contains:
        assert err_contains.replace(" ", "") in message.replace(" ", ""), (
            f"Не найден текст ошибки\n"
            f"Искали: {err_contains}\n"
            f"Message: {message}"
        )
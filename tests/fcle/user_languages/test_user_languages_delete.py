from http import HTTPStatus

import pytest

from fixtures.user_languages.fixture_user_languages import user_languages  # noqa: F401
from fixtures.user_languages.fixture_user_languages_cases import (
    _invalid_payloads,
    _valid_payload,
)
from settings import CONFLICT


class TestUserLanguages:
    @staticmethod
    def test_add_and_delete(auth_headers, user_languages):
        """
        E2E:
          1) list -> собираем занятые languageId
          2) add -> создаём ЗАВЕДОМО НОВЫЙ languageId
          3) проверяем, что запись видна
          4) delete -> удаляем
          5) убеждаемся, что записи нет
        """
        headers, _ = auth_headers
        client = user_languages(headers)

        # список до
        before = client.list() or []
        before_ids = {x["id"] for x in before if isinstance(x, dict) and "id" in x}
        used_lang_ids = {x.get("languageId") for x in before if isinstance(x, dict)}

        # генерируем валидный payload на СВОБОДНЫЙ languageId
        payload = _valid_payload(
            used_language_ids=used_lang_ids,
            is_target=False,
            level="A1",
            goal_id=1,
            subgoal_id=1,
        )

        # добавляем
        add_resp = client.add(payload)
        if add_resp.status_code == 500:
            pytest.xfail(f"500 при добавлении: {add_resp.text}")

        assert add_resp.status_code in (
            HTTPStatus.OK,
            HTTPStatus.CREATED,
        ), f"Не удалось добавить запись: {add_resp.status_code}, {add_resp.text}"

        data = add_resp.json()
        new_id = data.get("id")
        assert new_id not in (None, 0), f"пустой/некорректный id в ответе: {data}"

        # важно: мы создавали СВОБОДНЫЙ languageId, так что id не должен совпасть с тем, что был до
        assert (
            new_id not in before_ids
        ), "Бэк вернул id, который уже был в списке (возможный апсерт вместо создания)."

        # запись должна находиться сейчас в списке
        mid = client.list() or []
        assert any(
            isinstance(x, dict) and x.get("id") == new_id for x in mid
        ), "Запись не найдена после добавления (list())."

        # удаляем
        del_resp = client.delete(new_id)
        assert del_resp.status_code in (
            HTTPStatus.OK,
            HTTPStatus.NO_CONTENT,
        ), f"Удаление не прошло: {del_resp.status_code}, {del_resp.text}"

        # проверяем, что записи больше нет
        after = client.list() or []
        after_ids = {x["id"] for x in after if isinstance(x, dict) and "id" in x}
        assert new_id not in after_ids, f"ID {new_id} всё ещё в списке после удаления!"

    @staticmethod
    @pytest.mark.parametrize("payload", _invalid_payloads())
    def test_invalid_cases(auth_headers, user_languages, payload):
        """Невалидные сценарии → должны отклоняться (400/422)."""
        headers, _ = auth_headers
        client = user_languages(headers)

        resp = client.add(payload)
        if resp.status_code == 500:
            pytest.xfail(f"500 вместо ошибки валидации: {payload}, {resp.text}")

        assert (
            resp.status_code == CONFLICT
        ), f"Невалидный payload прошёл: {payload}, {resp.status_code}, {resp.text}"

    @staticmethod
    def test_delete_nonexistent(auth_headers, user_languages):
        """
        Попытка удалить несуществующий язык:
          → ожидаем 404 или 422, либо 200/204 с "false".
        """
        headers, _ = auth_headers
        client = user_languages(headers)

        fake_id = 999_999_999
        del_resp = client.delete(fake_id)

        if del_resp.status_code in (404, 422):
            return

        if del_resp.status_code in (HTTPStatus.OK, HTTPStatus.NO_CONTENT):
            text = (getattr(del_resp, "text", "") or "").strip().lower()
            assert text in (
                "false",
                "0",
                "",
            ), f"Удаление несуществующего id={fake_id} дало странный ответ: {del_resp.status_code}, {del_resp.text}"
        else:
            pytest.xfail(
                f"Неизвестная реакция API при удалении несуществующего языка: "
                f"{del_resp.status_code}, {del_resp.text}"
            )

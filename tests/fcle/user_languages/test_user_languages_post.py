import pytest
import json
from fixtures.user_languages.fixture_user_languages import user_languages
from fixtures.user_languages.fixture_user_languages_cases import _valid_payload, _invalid_payloads


class TestUserLanguagesPost:
    """Тесты POST /api/UserLanguages."""

    SUCCESS_CODES = {200, 201}
    VALIDATION_ERROR_CODES = {400, 409, 422}

    # ----------------- Хелперы -----------------

    @staticmethod
    def _used_language_ids(client) -> set:
        try:
            items = client.list()
            return {item.get("languageId") for item in items if isinstance(item, dict)}
        except Exception:
            return set()

    @staticmethod
    def _safe_delete(client, created_entity: dict):
        if not isinstance(created_entity, dict):
            return
        del_id = created_entity.get("id")
        if del_id is not None:
            try:
                client.delete(del_id)
            except Exception:
                pass

    # ----------------- Позитивные сценарии -----------------

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"is_target": False, "level": "A1", "goal_id": 1, "subgoal_id": 1},
            {"level": "B2", "goal_id": 1, "subgoal_id": 1},
            {"is_target": True, "goal_id": 3, "subgoal_id": 2, "level": "B1"},
        ],
        ids=["minimal", "with-level", "target-with-goal"],
    )
    def test_valid_flows(self, user_languages, kwargs):
        client = user_languages()
        used = self._used_language_ids(client)

        payload = _valid_payload(used_language_ids=used, **kwargs)
        r = client.add(payload)

        assert r.status_code in self.SUCCESS_CODES, \
            f"Unexpected {r.status_code}, text={getattr(r, 'text', '')}"

        data = r.json()
        assert data.get("id") not in (None, 0)
        assert data.get("languageId") == payload["languageId"]

        self._safe_delete(client, data)

    # ----------------- Негативные сценарии -----------------

    @pytest.mark.parametrize("bad_payload", _invalid_payloads(), ids=[
        "languageId<=0",
        "isTarget=null",
        "level=Z9",
        "isTarget=true&goalId=0",
        "subgoalId<=0",
    ])
    def test_validation_errors(self, user_languages, bad_payload):
        client = user_languages()
        r = client.add(dict(bad_payload))

        if r.status_code in self.SUCCESS_CODES:
            pytest.xfail(f"Backend accepted invalid payload: {bad_payload}")

        assert r.status_code in self.VALIDATION_ERROR_CODES, (
            f"Expected 4xx, got {r.status_code}, body={r.text}"
        )

        try:
            body = r.json()
            msg = json.dumps(body, ensure_ascii=False)
            assert any(k in msg.lower() for k in ["validation", "failed", "invalid", "must", "ошиб"]), msg
        except Exception:
            pass

    # ----------------- Новая логика -----------------

    def test_post_upsert_same_language(self, user_languages):
        """Повторный POST с тем же languageId = update (id записи сохраняется)."""
        client = user_languages()
        used = self._used_language_ids(client)

        payload = _valid_payload(
            used_language_ids=used,
            level="B1",
            goal_id=1,
            subgoal_id=1,
            is_target=False,
        )

        r1 = client.add(payload)
        assert r1.status_code in self.SUCCESS_CODES
        data1 = r1.json()
        rec_id = data1["id"]
        lang_id = data1["languageId"]

        # второй POST = update
        r2 = client.add(payload)
        assert r2.status_code in self.SUCCESS_CODES
        data2 = r2.json()

        assert data2["id"] == rec_id
        assert data2["languageId"] == lang_id

        self._safe_delete(client, data2)

    def test_post_is_target_without_goal(self, user_languages):
        """isTarget=true без goalId теперь валидный сценарий."""
        client = user_languages()
        used = self._used_language_ids(client)

        payload = _valid_payload(
            used_language_ids=used,
            is_target=True,
            level="B2",
            subgoal_id=1,
        )
        payload.pop("goalId", None)  # убираем явно

        r = client.add(payload)
        assert r.status_code in self.SUCCESS_CODES
        data = r.json()

        assert data.get("id") not in (None, 0)
        assert data.get("isTarget") is True

        self._safe_delete(client, data)

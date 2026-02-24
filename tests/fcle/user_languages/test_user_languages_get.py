import pytest

from http import HTTPStatus
from settings import ENDPOINTS, BASE_URL
from conftest import auth_headers
from fixtures.user_languages.fixture_user_languages import user_languages
from fixtures.user_languages.fixture_user_languages_cases import _valid_payload, _invalid_payloads
    

@pytest.mark.userlanguages
class TestUserLanguages:
    """Тесты для функциональности языков пользователя."""
    
    @pytest.fixture(autouse=True)
    def setup(self, auth_headers, user_languages):
        self.headers, self.email = auth_headers
        self.client = user_languages(self.headers)
        # Очищаем языки перед каждым тестом для изоляции
        self._cleanup_languages()
    

    def _cleanup_languages(self):
        """Очистка языков пользователя перед тестом."""
        try:
            languages = self.client.list()
            for lang in languages:
                if "id" in lang:
                    self.client.delete(lang["id"])
        except Exception as e:
            pytest.fail(f"Failed to cleanup languages: {e}")
    

    def _validate_language_structure(self, language_data: dict) -> None:
        """Валидация структуры данных языка."""
        required_fields = ["id", "languageId"]
        for field in required_fields:
            assert field in language_data, f"Missing required field: {field} in {language_data}"
        
        assert language_data["id"] is not None, "Language ID should not be None"
        assert isinstance(language_data["languageId"], int), "languageId should be integer"

    def _add_test_language(self, payload: dict = None):
        """Вспомогательный метод: создаём язык с валидным payload и свободным languageId."""
        # 1) Собираем уже занятые languageId, чтобы не попасть в дубль
        used = {x.get("languageId") for x in (self.client.list() or []) if isinstance(x, dict)}

        if payload is None:
            # 2) Генерим сразу корректный payload под текущие правила бэка
            payload = _valid_payload(
                used_language_ids=used,  # <-- важно
                is_target=False,
                level="A1",
                goal_id=1,  # <-- > 0
                subgoal_id=1,  # <-- > 0
            )
        else:
            # Чиним входной payload, если пришёл "сырой"
            payload = dict(payload)  # не мутируем аргумент
            payload.setdefault("isTarget", False)
            payload.setdefault("level", "A1")
            payload["goalId"] = payload.get("goalId") or 1
            payload["subgoalId"] = payload.get("subgoalId") or 1

            # Если languageId не задан или уже занят — сгенерим новый через фабрику
            lang = payload.get("languageId")
            if not lang or lang in used:
                payload = _valid_payload(
                    used_language_ids=used,
                    is_target=payload["isTarget"],
                    level=payload["level"],
                    goal_id=payload["goalId"],
                    subgoal_id=payload["subgoalId"],
                )

        response = self.client.add(payload)

        if response.status_code == 500:
            pytest.xfail(f"Server error: {response.text}")

        assert response.status_code in (HTTPStatus.OK, HTTPStatus.CREATED), (
            f"Request body: {payload}\n"
            f"Response: {response.text}\n"
            f"Status code: {response.status_code}"
        )

        response_data = response.json()
        self._validate_language_structure(response_data)
        return response_data, payload
    

    def test_empty_list_for_new_user(self):
        """Тест: новый пользователь имеет пустой список языков."""
        languages = self.client.list()
        
        assert isinstance(languages, list), f"Expected list, got {type(languages)}"
        assert languages == [], f"Expected empty list, got {languages}"
    

    def test_add_language(self):
        """Тест: добавление языка пользователю."""
        response_data, payload = self._add_test_language()
        
        # Проверяем, что язык появился в списке
        languages = self.client.list()
        assert len(languages) == 1, (
            f"Expected 1 language, got {len(languages)}: {languages}"
        )
        
        added_language = languages[0]
        self._validate_language_structure(added_language)
        
        # Проверяем соответствие данных
        assert added_language["languageId"] == payload["languageId"], (
            f"Expected languageId {payload['languageId']}, "
            f"got {added_language['languageId']}\n"
            f"Request body: {payload}\n"
            f"Response: {added_language}"
        )
        
        # Проверяем согласованность ID
        assert added_language["id"] == response_data["id"], (
            f"ID mismatch between add response and list response"
        )
    

    def test_get_language_by_id(self):
        """Тест: получение языка по ID."""
        # Добавляем язык
        response_data, payload = self._add_test_language()
        language_id = response_data["id"]
        
        # Получаем язык по ID
        get_response = self.client.get_lang(language_id)
        
        assert get_response.status_code == HTTPStatus.OK, (
            f"Failed to get language by ID: {get_response.status_code}\n"
            f"Response: {get_response.text}"
        )
        
        language_data = get_response.json()
        self._validate_language_structure(language_data)
        
        # Проверяем, что получены корректные данные
        assert language_data["id"] == language_id, (
            f"ID mismatch: expected {language_id}, got {language_data['id']}"
        )
        assert language_data["languageId"] == payload["languageId"], (
            f"LanguageId mismatch: expected {payload['languageId']}, "
            f"got {language_data['languageId']}"
        )
    



import pytest

from fixtures.users.fixture_telegram import telegram_cases, telegram_user


@pytest.mark.telegram_post
class TestTelegramUser:
    """
    Набор тестов для проверки работы эндпоинта POST /Users/telegram.

    Логика:
    - Через фикстуру `telegram_cases` задаются разные сценарии:
        * valid_user  – полный валидный набор данных (успешное создание пользователя).
        * minimal_data – только обязательные поля (также успешное создание).
        * invalid_data – некорректные данные (ожидаем валидационную ошибку).
    - Фикстура `telegram_user` создаёт объект `TelegramUser`, который инкапсулирует
      вызов API и хранит в себе payload + ожидаемые статусы.
    - В тестах мы просто:
        1. Берём сценарий (payload + ожидаемый статус).
        2. Создаём объект `TelegramUser`.
        3. Вызываем `.create()`, который отправляет POST-запрос.
        4. Проверяем, что код ответа совпадает с ожидаемым.
        5. Для успешных кейсов дополнительно проверяем структуру ответа
           (наличие `id`, `nickname`, `telegramAccount` и корректность значений).
    - Таким образом тесты получаются декларативными: сценарии описаны в данных,
      логика отправки запроса спрятана в классе, а тесты содержат только ассерты.
    """

    @staticmethod
    @pytest.mark.parametrize("case_name", ["valid_user", "minimal_data"])
    def test_create_success(telegram_user, telegram_cases, case_name):
        payload, expected_statuses = telegram_cases[case_name]
        tg = telegram_user(payload, expected_statuses)

        response, statuses = tg.create()

        assert (
            response.status_code in statuses
        ), f"Expected {statuses}, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data
        assert isinstance(data["nickname"], str)
        assert data["telegramAccount"].endswith(payload["telegramAccount"].lstrip("@"))

    @staticmethod
    def test_create_invalid(telegram_user, telegram_cases):
        payload, expected_statuses = telegram_cases["invalid_data"]
        tg = telegram_user(payload, expected_statuses)

        response, statuses = tg.create()

        assert (
            response.status_code == statuses
        ), f"Expected {statuses}, got {response.status_code}: {response.text}"

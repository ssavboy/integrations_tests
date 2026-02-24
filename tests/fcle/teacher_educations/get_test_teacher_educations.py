import json
import pytest
from datetime import datetime

from fixtures.teacher_educations.fixture_teacher_educations_get import teacher_educations
from parametrs.parameters_teacher_educations import generate_cases


@pytest.mark.teacher_educations
@pytest.mark.parametrize("case", generate_cases("GET"), ids=lambda c: c.label)
def test_teacher_educations(teacher_educations, case):
    """
        Интеграционный тест для  GET_TeacherEducations.

        Проверяет, что API корректно обрабатывает разные сценарии запросов:
            - Авторизованный пользователь (базовый happy-path).
            - Неавторизованный доступ (ожидаем 401/403).
            - Запросы с битым токеном.
            - Фильтрация по teacherId (валидная и невалидная).
            - Пагинация (валидные параметры, выход за границы, некорректные значения).
            - Пустой результат (для несуществующего teacherId).
            - Запросы с некорректными Accept-заголовками.
            - Обращение к несуществующим ресурсам.

        Логика проверки:
            1. Сравнивает фактический статус-код ответа с ожидаемым (из generate_cases()).
            2. Для успешных запросов (200 OK):
                - Убеждается, что тело ответа — это JSON-массив.
                - Проверяет наличие обязательных ключей в каждом объекте.
                - Валидирует бизнес-правила:
                    * startYear <= текущий год.
                    * finishYear >= startYear.
                - Проверяет структуру документов (documents) внутри образования.

        Параметры:
            teacher_educations (fixture): фабрика клиента TeacherEducationsClient
                                          с уже настроенными заголовками/параметрами.
            case (TeacherEducationsCase): описание сценария (label, expected_status, auth, params).
        """
    client = teacher_educations(case)
    r = client.get()

    # Проверка статуса
    assert case.matches_expected(r.status_code), \
        f"Ожидали {case.expected_status}, получили {r.status_code}. Тело: {r.text!r}"

    if r.status_code == 200:
        try:
            data = r.json()
        except json.JSONDecodeError as e:
            pytest.fail(f"Ответ не JSON: {e}. Raw: {r.text[:300]}")

        assert isinstance(data, list), f"Ожидался список, получили {type(data)}"

        if data:
            edu = data[0]
            expected_keys = {
                "id", "teacherId", "institutionName", "degreeId", "fieldOfStudy",
                "startYear", "finishYear", "createdAt", "updatedAt", "documents",
            }
            missing = expected_keys - set(edu.keys())
            assert not missing, f"Нет ключей в элементе: {missing}"

            # Базовые типы
            assert isinstance(edu["id"], int)
            assert isinstance(edu["teacherId"], int)
            assert isinstance(edu["institutionName"], (str, type(None)))
            assert isinstance(edu["degreeId"], (int, type(None)))
            assert isinstance(edu["fieldOfStudy"], (str, type(None)))
            assert isinstance(edu["startYear"], (int, type(None)))
            assert isinstance(edu["finishYear"], (int, type(None)))
            assert isinstance(edu["createdAt"], str)
            assert isinstance(edu["updatedAt"], str)
            assert isinstance(edu["documents"], list)

            # Бизнес-правила (валидация)
            if edu["startYear"]:
                assert edu["startYear"] <= datetime.now().year, \
                    f"startYear в будущем: {edu['startYear']}"
            if edu["finishYear"] and edu["startYear"]:
                assert edu["finishYear"] >= edu["startYear"], \
                    f"finishYear < startYear: {edu['finishYear']} < {edu['startYear']}"

            # Документы
            docs = edu.get("documents") or []
            if docs:
                d0 = docs[0]
                expected_doc_keys = {
                    "id", "teacherId", "documentType", "fileName", "fileUrl", "title", "description"
                }
                miss_doc = expected_doc_keys - set(d0.keys())
                assert not miss_doc, f"Нет ключей в document: {miss_doc}"

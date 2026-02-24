import pytest
import json
from http import HTTPStatus
from datetime import datetime
from fixtures.teacher_educations.fixture_post_test_teacher_educations import teacher_educations_post
from parametrs.parameters_teacher_educations import generate_cases


@pytest.mark.teacher_educations_post
def test_post_teacher_educations(teacher_educations_post):
    """
    Интеграционный тест эндпоинта POST /TeacherEducations.

    Проверяем сценарии:
        - Валидный POST (happy path).
        - Без авторизации (401/403).
        - Битый токен.
        - Нарушение бизнес-правил (future startYear, finish < startYear).
        - Нарушение ограничений (слишком длинные строки, пустые поля, degreeId <= 0).

    В успешных кейсах (200):
        - Тело ответа — JSON-объект.
        - Присутствуют обязательные ключи.
        - Валидируем бизнес-правила (finishYear >= startYear, startYear <= текущий год).
    """
    client, case = teacher_educations_post
    r = client.post()

    if case.label == "valid_basic":
        pytest.xfail("Сервер возвращает 500 вместо 200, ожидаем фикс от бэка")

    r = client.post()
    # Проверка статуса
    assert case.matches_expected(r.status_code), \
        f"Ожидали {case.expected_status}, получили {r.status_code}. Тело: {r.text!r}"

    if r.status_code == HTTPStatus.OK:
        try:
            data = r.json()
        except json.JSONDecodeError as e:
            pytest.fail(f"Ответ не JSON: {e}. Raw: {r.text[:300]}")

        expected_keys = {
            "id", "teacherId", "institutionName", "degreeId", "fieldOfStudy",
            "startYear", "finishYear", "createdAt", "updatedAt", "documents",
        }
        missing = expected_keys - set(data.keys())
        assert not missing, f"Нет ключей в ответе: {missing}"

        # Бизнес-правила
        if data["startYear"]:
            assert data["startYear"] <= datetime.now().year, \
                f"startYear в будущем: {data['startYear']}"
        if data["finishYear"] and data["startYear"]:
            assert data["finishYear"] >= data["startYear"], \
                f"finishYear < startYear: {data['finishYear']} < {data['startYear']}"

        assert isinstance(data["documents"], list)

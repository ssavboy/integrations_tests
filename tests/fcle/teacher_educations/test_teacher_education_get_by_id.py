import json
import pytest
from datetime import datetime

from fixtures.teacher_educations.fixture_teacher_education_get_by_id import teacher_education_by_id
from parametrs.parameters_teacher_educations_by_id import generate_cases_by_id

@pytest.mark.teacher_educations
@pytest.mark.parametrize("case", generate_cases_by_id(), ids=lambda c: c.label)
def test_teacher_education_get_by_id(teacher_education_by_id, case):
    """
    Интеграционный тест для GET /TeacherEducations/{id}.
    Проверяем авторизацию, существующие/несуществующие id и валидации.
    """
    client = teacher_education_by_id(case)
    r = client.get()

    # Статус-код по ожиданию
    assert case.matches_expected(r.status_code), \
        f"{case.label}: ожидали {case.expected_status}, получили {r.status_code}. body={r.text!r}"

    # Для 200 — проверяем схему (JSON-объект с полями образования)
    if r.status_code == 200:
        try:
            data = r.json()
        except json.JSONDecodeError as e:
            pytest.fail(f"{case.label}: Ответ не JSON: {e}. Raw: {r.text[:300]}")

        # Базовая структура
        expected_keys = {
            "id", "teacherId", "institutionName", "degreeId", "fieldOfStudy",
            "startYear", "finishYear", "createdAt", "updatedAt", "documents",
        }
        missing = expected_keys - set(data.keys())
        assert not missing, f"{case.label}: нет ключей {missing}"

        # Типы
        assert isinstance(data["id"], int)
        assert isinstance(data["teacherId"], int)
        assert isinstance(data["institutionName"], (str, type(None)))
        assert isinstance(data["degreeId"], (int, type(None)))
        assert isinstance(data["fieldOfStudy"], (str, type(None)))
        assert isinstance(data["startYear"], (int, type(None)))
        assert isinstance(data["finishYear"], (int, type(None)))
        assert isinstance(data["createdAt"], str)
        assert isinstance(data["updatedAt"], str)

        # 🔻 Временный xfail из-за бага бэка:
        # Бэк возвращает documents = null вместо пустого массива [].
        docs = data.get("documents")
        if docs is None:
            pytest.xfail("BUG: API возвращает documents=null вместо []. Помечаем xfail до фикса бэка.")

        # Строгое ожидание после фикса: список
        assert isinstance(docs, list), f"{case.label}: documents должен быть list, получено {type(docs).__name__}"

        # Бизнес-правила
        if data["startYear"] is not None:
            assert data["startYear"] <= datetime.now().year, \
                f"{case.label}: startYear в будущем: {data['startYear']}"
        if data["startYear"] is not None and data["finishYear"] is not None:
            assert data["finishYear"] >= data["startYear"], \
                f"{case.label}: finishYear < startYear"

        # Документы (если есть)
        if docs:
            doc0 = docs[0]
            expected_doc_keys = {
                "id", "teacherId", "documentType", "fileName", "fileUrl", "title", "description"
            }
            miss_doc = expected_doc_keys - set(doc0.keys())
            assert not miss_doc, f"{case.label}: нет ключей в document: {miss_doc}"

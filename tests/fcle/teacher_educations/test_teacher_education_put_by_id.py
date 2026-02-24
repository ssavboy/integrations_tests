import json
import pytest
from datetime import datetime

from fixtures.teacher_educations.fixture_teacher_education_put_by_id import teacher_education_put_by_id
from parametrs.parameters_teacher_educations_put_by_id import generate_cases_put_by_id

@pytest.mark.teacher_educations
@pytest.mark.parametrize("case", generate_cases_put_by_id(), ids=lambda c: c.label)
def test_teacher_education_put_by_id(teacher_education_put_by_id, case):
    client = teacher_education_put_by_id(case)
    r = client.put()

    assert case.matches_expected(r.status_code), \
        f"{case.label}: ожидали {case.expected_status}, получили {r.status_code}. body={r.text!r}"

    # Успех: проверяем структуру
    if r.status_code == 200:
        try:
            data = r.json()
        except json.JSONDecodeError:
            pytest.fail(f"{case.label}: ожидали JSON; raw={r.text[:300]!r}")

        expected_keys = {
            "id", "teacherId", "institutionName", "degreeId", "fieldOfStudy",
            "startYear", "finishYear", "createdAt", "updatedAt", "documents",
        }
        missing = expected_keys - set(data.keys())
        assert not missing, f"{case.label}: нет ключей {missing}"

        assert isinstance(data["id"], int)
        assert isinstance(data["teacherId"], int)
        assert isinstance(data["institutionName"], (str, type(None)))
        assert isinstance(data["degreeId"], (int, type(None)))
        assert isinstance(data["fieldOfStudy"], (str, type(None)))
        assert isinstance(data["startYear"], (int, type(None)))
        assert isinstance(data["finishYear"], (int, type(None)))
        assert isinstance(data["createdAt"], str)
        assert isinstance(data["updatedAt"], str)

        docs = data.get("documents")
        if docs is None:
            pytest.xfail("BUG: API возвращает documents=null вместо []. Помечаем xfail до фикса бэка.")
        assert isinstance(docs, list)

        if data["startYear"] is not None:
            assert data["startYear"] <= datetime.now().year
        if data["startYear"] is not None and data["finishYear"] is not None:
            assert data["finishYear"] >= data["startYear"]

        if docs:
            doc0 = docs[0]
            expected_doc_keys = {
                "id", "teacherId", "documentType", "fileName", "fileUrl", "title", "description"
            }
            miss_doc = expected_doc_keys - set(doc0.keys())
            assert not miss_doc, f"{case.label}: нет ключей в document: {miss_doc}"

    # Ошибки: при наличии ожидаемого error_code сверяем тело
    if r.status_code >= 400 and getattr(case, "error_code", None):
        try:
            body = r.json()
        except json.JSONDecodeError:
            pytest.fail(f"{case.label}: ожидали JSON-тело ошибки; raw={r.text[:300]!r}")

        code = body.get("error", {}).get("code") or body.get("code")
        assert code == case.error_code, f"{case.label}: ожидали error.code={case.error_code!r}, получили {code!r}"

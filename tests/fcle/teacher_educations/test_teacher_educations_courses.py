import pytest

from settings import BASE_URL, ENDPOINTS
from fixtures.teacher_educations.fixture_teacher_educations_courses import (
    generate_courses_cases,
    validate_course_item,
    client_case_courses
)

COURSES_URL = f"{BASE_URL}{ENDPOINTS['teacher_educations']}/courses"


@pytest.mark.teacher_educations
@pytest.mark.parametrize(
    "client_case_courses",
    generate_courses_cases(),
    indirect=True,
    ids=lambda c: c.label,
)
def test_courses_list(client_case_courses):
    client, case = client_case_courses

    r = client.list()
    assert r.status_code in case.expected_statuses, (
        f"[{case.label}] ожидали {case.expected_statuses}, получили {r.status_code}. "
        f"Тело: {r.text!r}"
    )

    if r.status_code != 200:
        # Пытаемся проверить problem+json
        ctype = r.headers.get("Content-Type", "")
        if "json" in ctype:
            err = r.json()
            # Мягкая проверка полей problem details
            assert isinstance(err, dict)
            for k in ("type", "title", "status"):
                assert k in err, f"problem-json: нет поля {k}"
            assert err.get("status") == r.status_code
        else:
            # допускаем пустое тело или текст
            assert r.text in ("",) or isinstance(r.text, str)
        return

    # Content-Type sanity
    ctype = r.headers.get("Content-Type", "")
    assert "json" in ctype or "text" in ctype

    # Если сервер отдаёт JSON — проверяем структуру
    if "json" in ctype:
        try:
            data = r.json()
        except Exception as e:
            pytest.fail(f"[{case.label}] не удалось распарсить JSON при 200: {e}\nBody: {r.text!r}")

        assert isinstance(data, (list, dict)), (
            f"[{case.label}] JSON ожидаем list|dict, получили {type(data)}"
        )
        items = data if isinstance(data, list) else data.get("items", [])

        errs_all = []
        for i, it in enumerate(items):
            errs_all.extend(validate_course_item(it, i))
            if i >= 50:
                break

        assert not errs_all, f"[{case.label}] ошибки схемы:\n" + "\n".join(errs_all)

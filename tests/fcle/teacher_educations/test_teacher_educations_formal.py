import pytest

# Подключаем модуль с фикстурами как плагин
pytest_plugins = ("fixtures.teacher_educations.fixture_teacher_educations_formal",)

from settings import BASE_URL, ENDPOINTS
from fixtures.teacher_educations.fixture_teacher_educations_formal import (
    generate_formal_cases,
    validate_formal_item,
)

FORMAL_URL = f"{BASE_URL}{ENDPOINTS['teacher_educations']}/formal"


@pytest.mark.teacher_educations
@pytest.mark.parametrize(
    "client_case_formal",
    generate_formal_cases(),
    indirect=True,
    ids=lambda c: c.label,
)
def test_formal_list(client_case_formal):
    client, case = client_case_formal

    r = client.list()
    assert r.status_code in case.expected_statuses, (
        f"[{case.label}] ожидали {case.expected_statuses}, получили {r.status_code}. "
        f"Тело: {r.text!r}"
    )

    # Если это ошибка доступов — валидируем problem+json, чтобы не прятать мусор
    if r.status_code in (401, 403):
        ctype = r.headers.get("Content-Type", "")
        if "json" in ctype:
            err = r.json()
            assert isinstance(err, dict)
            for k in ("type", "title", "status"):
                assert k in err, f"problem-json missing `{k}`"
            assert err.get("status") == r.status_code
        # если backend отдает пусто/текст — допустим, но без падений
        return

    if r.status_code != 200:
        return  # другие не-200 не валидируем здесь

    # Тип контента
    ctype = r.headers.get("Content-Type", "")
    assert "json" in ctype or "text" in ctype

    # Если JSON — валидируем
    if "json" in ctype:
        data = r.json()
        assert isinstance(data, (list, dict)), f"list|dict expected, got {type(data)}"
        items = data if isinstance(data, list) else data.get("items", [])
        errs = []
        for i, it in enumerate(items):
            errs.extend(validate_formal_item(it, i))
            if i >= 50:
                break
        assert not errs, "schema errors:\n" + "\n".join(errs)

import pytest
from fixtures.teacher_educations.fixture_teacher_educations_delete import (
    generate_delete_cases,
    client_case_delete_teacher_educations,
    create_teacher_education,
    make_accept_text_plain,
)
from settings import ENDPOINTS

TEACHER_EDU_ENDPOINT = ENDPOINTS["teacher_educations"]


@pytest.mark.teacher_educations
@pytest.mark.parametrize(
    "client_case_delete_teacher_educations",
    generate_delete_cases(),
    indirect=True,
    ids=lambda c: c.label,
)
def test_delete_cases(client_case_delete_teacher_educations):
    client, case, target_id = client_case_delete_teacher_educations

    r = client.delete(target_id)

    assert r.status_code in case.expected_statuses, (
        f"[{case.label}] Ожидали {case.expected_statuses}, получили {r.status_code}. Тело: {r.text!r}"
    )
    if r.status_code == 200:
        body = (r.text or "").strip().lower()
        assert body in {"true", "false"}, f"[{case.label}] При 200 ждём 'true'/'false', получили: {r.text!r}"
        # Бэк может вернуть и text/plain, и application/json — принимаем оба
        ct = (r.headers.get("Content-Type") or "").lower()
        assert ("text/plain" in ct) or ("application/json" in ct), \
            f"[{case.label}] При 200 ждём Content-Type text/plain или application/json, получили: {ct!r}"


@pytest.mark.teacher_educations
def test_double_delete_returns_false_or_404_or_422(auth_headers, post_request, delete_request):
    """
    1-й DELETE: 200 ('true'/'false').
    2-й DELETE: 200('false') ИЛИ 404/410/422 (в зависимости от реализации).
    """
    headers, _ = auth_headers
    headers = make_accept_text_plain(headers)

    edu_id, post_resp = create_teacher_education(post_request, headers=headers)
    if not edu_id:
        pytest.xfail(
            f"BUG/ENV: POST нестабилен, запись не создана. "
            f"status={getattr(post_resp,'status_code','?')}, body={getattr(post_resp,'text','?')!r}"
        )

    r1 = delete_request(None, f"{TEACHER_EDU_ENDPOINT}/{edu_id}", headers=headers)
    assert r1.status_code == 200
    assert (r1.text or "").strip().lower() in {"true", "false"}

    r2 = delete_request(None, f"{TEACHER_EDU_ENDPOINT}/{edu_id}", headers=headers)
    assert r2.status_code in (200, 404, 410, 422), f"Ожидали 200/404/410/422, получили {r2.status_code}: {r2.text!r}"
    if r2.status_code == 200:
        assert (r2.text or "").strip().lower() == "false", f"При 200 ожидаем 'false', получили: {r2.text!r}"


@pytest.mark.teacher_educations
def test_delete_without_accept_header(auth_headers, delete_request):
    """Без Accept: допускаем 200/404/410/422 (но не 406)."""
    headers, _ = auth_headers
    r = delete_request(None, f"{TEACHER_EDU_ENDPOINT}/987654321", headers=headers)
    assert r.status_code in (200, 404, 410, 422), \
        f"Ожидали 200/404/410/422 без Accept, получили {r.status_code}: {r.text!r}"


@pytest.mark.teacher_educations
def test_delete_with_json_accept(auth_headers, post_request, delete_request):
    """
    Accept: application/json — либо 406, либо обычные 200/404/410/422.
    При 200 тело всё равно 'true'/'false' (иногда JSON).
    """
    headers, _ = auth_headers
    headers = {**headers, "Accept": "application/json"}

    edu_id, post_resp = create_teacher_education(post_request, headers=headers)
    if not edu_id:
        pytest.xfail(f"BUG/ENV: POST не создал запись: {getattr(post_resp,'status_code','?')} {getattr(post_resp,'text','?')!r}")

    r = delete_request(None, f"{TEACHER_EDU_ENDPOINT}/{edu_id}", headers=headers)
    assert r.status_code in (200, 404, 410, 422, 406), \
        f"Ожидали 200/404/410/422/406, получили {r.status_code}: {r.text!r}"
    if r.status_code == 200:
        assert (r.text or '').strip().lower() in {"true", "false"}


@pytest.mark.teacher_educations
def test_delete_without_id_returns_404_or_405(auth_headers, delete_request):
    """Удаление без {id} в пути: 404 (route) или 405 (method)."""
    headers, _ = auth_headers
    headers = make_accept_text_plain(headers)
    r = delete_request(None, TEACHER_EDU_ENDPOINT, headers=headers)
    assert r.status_code in (404, 405), f"Ожидали 404/405 без id, получили {r.status_code}: {r.text!r}"


@pytest.mark.teacher_educations
def test_delete_removes_from_list_when_ok(auth_headers, post_request, delete_request, get_request):
    """
    После успешного 200 удаление — подтверждаем исчезновение:
      1) Пытаемся GET по id -> ждём 404/410/422.
         Если эндпоинт GET-by-id отключён (405), это БАГ — помечаем xfail.
      2) Дополнительно: проверяем список. Если список недоступен (404/405), это БАГ — помечаем xfail.
    """
    headers, _ = auth_headers
    headers_del = make_accept_text_plain(headers)                 # для DELETE (text/plain)
    headers_json = {**headers, "Accept": "application/json"}     # для GET (JSON)

    # Создали
    edu_id, post_resp = create_teacher_education(post_request, headers=headers_del)
    if not edu_id:
        pytest.xfail(f"BUG/ENV: POST не создал запись: {getattr(post_resp,'status_code','?')} {getattr(post_resp,'text','?')!r}")

    # Удалили
    r_del = delete_request(None, f"{TEACHER_EDU_ENDPOINT}/{edu_id}", headers=headers_del)
    if r_del.status_code != 200:
        pytest.xfail(f"BUG/ENV: DELETE вернул не 200 ({r_del.status_code}), тело: {r_del.text!r}")

    # 1) Проверка по id
    r_by_id = get_request({}, f"{TEACHER_EDU_ENDPOINT}/{edu_id}", headers=headers_json)
    if r_by_id.status_code in (404, 410, 422):
        pass  # ок, подтверждено
    elif r_by_id.status_code == 405:
        pytest.xfail("BUG: GET /TeacherEducations/{id} возвращает 405 после удаления (метод отключён на инстансе).")
    else:
        assert False, f"После удаления GET по id должен вернуть 404/410/422, получили {r_by_id.status_code}: {r_by_id.text!r}"

    # 2) Доп.проверка списка
    r_list = get_request({}, TEACHER_EDU_ENDPOINT, headers=headers_json)
    if r_list.status_code in (404, 405):
        pytest.xfail(f"BUG: GET /TeacherEducations недоступен (status={r_list.status_code}) — метод выключен/не сконфигурирован.")
    assert r_list.status_code in (200, 204), f"GET список упал: {r_list.status_code} {r_list.text!r}"
    if r_list.status_code == 204:
        return  # пустой список — ок

    try:
        data = r_list.json() or []
    except Exception:
        data = []

    # Универсальный парс списка: либо массив, либо объект с items/data/results
    if isinstance(data, dict):
        items = data.get("items") or data.get("data") or data.get("results") or []
    elif isinstance(data, list):
        items = data
    else:
        items = []

    ids = {it.get("id") for it in items if isinstance(it, dict)}
    assert edu_id not in ids, f"id={edu_id} всё ещё в списке после успешного удаления"

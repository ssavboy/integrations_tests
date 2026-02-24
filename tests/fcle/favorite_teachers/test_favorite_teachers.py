import pytest
from http import HTTPStatus
from fixtures.teachers.fixture_favorite_teachers import fav_teachers

ID_A = 1000155
ID_B = 1000144

@pytest.mark.favorite_teachers
def test_add_and_list_multiple_teachers(auth_headers, fav_teachers):
    """
    Test adding and retrieving multiple favorite teachers.

    This test verifies that the API correctly handles adding more than one
    teacher to the list of favorites and that they can subsequently be retrieved
    via the GET endpoint.

    Args:
        auth_headers (tuple): Fixture providing (headers, email) for an authenticated user.
        fav_teachers (fixture): Factory fixture returning a Client wrapper for the
                                FavoriteTeachers API (with add, list, delete, clear methods).

    Steps:
        1. Authenticate and get an API client via `fav_teachers`.
        2. Call `clear()` to ensure the favorites list starts empty.
        3. Add two known teacher IDs (`ID_A`, `ID_B`) with `add_many`.
        4. Call `list()` to retrieve the current favorite teachers.
        5. Verify that both IDs are present in the returned list.

    Assertions:
        - Both `ID_A` and `ID_B` exist in the returned set of teacher IDs.
        - The list of favorites contains at least the added teachers.

    Fails if:
        - One or both teacher IDs are missing from the retrieved list.
        - The API fails to persist multiple additions.
    """
    headers, _ = auth_headers
    api = fav_teachers(headers)

    api.clear()
    api.add_many([ID_A, ID_B])

    data = api.list()
    returned_ids = {t["id"] for t in (data or [])}
    assert {ID_A, ID_B}.issubset(returned_ids), \
        f"Expected {ID_A, ID_B}, got {returned_ids}"


@pytest.mark.favorite_teachers
def test_get_structure_has_expected_fields(auth_headers, fav_teachers):
    """
    Test that the FavoriteTeachers API response has the expected structure.

    This test ensures that when retrieving the list of favorite teachers,
    each item in the response contains mandatory top-level fields
    (`id`, `nickname`, `language`), and that the `language` field itself
    is a dictionary with the expected nested keys.

    Args:
        auth_headers (tuple): Fixture providing (headers, email) for an authenticated user.
        fav_teachers (fixture): Factory fixture returning a Client wrapper for the
                                FavoriteTeachers API.

    Steps:
        1. Authenticate and create an API client via `fav_teachers`.
        2. Clear any existing favorites for a clean start.
        3. Add a single known teacher (ID_A).
        4. Retrieve the favorites list.
        5. Inspect the first item in the list and check:
            - It contains `id`, `nickname`, and `language`.
            - The `language` field is a dictionary.
            - That dictionary contains `id`, `languageName`, and `languageOwnName`.

    Assertions:
        - Response is a list with at least one teacher object.
        - Each teacher object has the required top-level keys.
        - The `language` object is structured correctly with the required fields.

    Fails if:
        - Response is not a list or is empty.
        - Required keys are missing in the teacher object.
        - The `language` field is not a dict or lacks its expected subfields.
    """
    headers, _ = auth_headers
    api = fav_teachers(headers)

    api.clear()
    api.add(ID_A)

    items = api.list()
    assert isinstance(items, list) and len(items) >= 1
    sample = items[0]

    for key in ("id", "nickname", "language"):
        assert key in sample, f"Item doesnt have field '{key}': {sample}"
    assert isinstance(sample["language"], dict)
    for key in ("id", "languageName", "languageOwnName"):
        assert key in sample["language"], f"Language doesnt have field '{key}': {sample['language']}"


@pytest.mark.favorite_teachers
def test_delete_single_teacher(auth_headers, fav_teachers):
    """
    Test deleting a single teacher from favorites.

    This test verifies that when multiple teachers are added to the
    favorites list, deleting one teacher by ID removes only that teacher
    while leaving the others intact.

    Args:
        auth_headers (tuple): Fixture providing (headers, email) for an authenticated user.
        fav_teachers (fixture): Factory fixture returning a Client wrapper for the
                                FavoriteTeachers API.

    Steps:
        1. Authenticate and create an API client via `fav_teachers`.
        2. Clear the favorites list to ensure a clean test state.
        3. Add two teachers (ID_A and ID_B).
        4. Delete one teacher (ID_A) by ID.
        5. Retrieve the updated favorites list.
        6. Verify that ID_A has been removed but ID_B remains.

    Assertions:
        - The deleted teacher ID (ID_A) is not present in the list.
        - The other teacher ID (ID_B) is still present.

    Fails if:
        - Both teachers are removed.
        - The deleted teacher ID still appears in the favorites list.
    """
    headers, _ = auth_headers
    api = fav_teachers(headers)

    api.clear()
    api.add_many([ID_A, ID_B])

    api.delete(ID_A)
    left = {t["id"] for t in (api.list() or [])}
    assert ID_A not in left and ID_B in left


@pytest.mark.favorite_teachers
def test_delete_multiple_teachers(auth_headers, fav_teachers):
    """
    Test deleting multiple teachers from favorites.

    This test verifies that when several teachers are added to the
    favorites list, deleting a subset of them by IDs removes exactly
    those teachers while leaving the others intact.

    Args:
        auth_headers (tuple): Fixture providing (headers, email) for an authenticated user.
        fav_teachers (fixture): Factory fixture returning a Client wrapper for the
                                FavoriteTeachers API.

    Steps:
        1. Authenticate and create an API client via `fav_teachers`.
        2. Clear the favorites list to ensure a clean test state.
        3. Add two teachers (ID_A and ID_B).
        4. Call `delete_many` with a list containing only ID_A.
        5. Retrieve the updated favorites list.
        6. Verify that ID_A has been removed but ID_B remains.

    Assertions:
        - The deleted teacher ID (ID_A) is not present in the list.
        - The other teacher ID (ID_B) is still present.

    Fails if:
        - Both teachers are removed.
        - The deleted teacher ID still appears in the favorites list.
    """
    headers, _ = auth_headers
    api = fav_teachers(headers)

    api.clear()
    api.add_many([ID_A, ID_B])

    api.delete_many([ID_A])
    left = {t["id"] for t in (api.list() or [])}
    assert ID_A not in left and ID_B in left


@pytest.mark.favorite_teachers
def test_delete_is_not_idempotent_but_safe(auth_headers, fav_teachers):
    """
    Test repeated deletion of the same teacher from favorites.

    This test ensures that deleting an existing teacher works as expected
    (removing them from the list), and that attempting to delete the same teacher
    again does not break the API. Depending on the backend implementation, the second
    deletion may return either:
      - 200 OK / 204 No Content (idempotent behavior), or
      - 422 Unprocessable Entity with a `notFound` code (non-idempotent, but still safe).

    Args:
        auth_headers (tuple): Fixture providing (headers, email) for an authenticated user.
        fav_teachers (fixture): Factory fixture returning a Client wrapper for the
                                FavoriteTeachers API.

    Steps:
        1. Authenticate and create an API client via `fav_teachers`.
        2. Clear the favorites list to start from a clean state.
        3. Add a single teacher (ID_A).
        4. Delete this teacher once — expect 200/204.
        5. Attempt to delete the same teacher again.
           - Accept 200/204 (idempotent) or 422 with "notFound".
        6. Fetch the current favorites list and confirm that the teacher is absent.

    Assertions:
        - First deletion returns 200 or 204.
        - Second deletion returns 200/204 or 422 with `notFound` in response body.
        - The deleted teacher ID is not in the favorites list.

    Fails if:
        - First deletion fails.
        - Second deletion returns an unexpected status.
        - The teacher still appears in the favorites list.
    """
    headers, _ = auth_headers
    api = fav_teachers(headers)

    api.clear()
    api.add(ID_A)

    r1 = api.delete(ID_A)
    assert r1.status_code in (HTTPStatus.OK, HTTPStatus.NO_CONTENT)

    r2 = api.delete_ignore_missing(ID_A)
    assert r2.status_code in (HTTPStatus.OK, HTTPStatus.NO_CONTENT, HTTPStatus.UNPROCESSABLE_ENTITY)
    if r2.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        assert "notFound" in (r2.text or "")

    assert ID_A not in {t["id"] for t in (api.list() or [])}


@pytest.mark.favorite_teachers
def test_add_duplicate_returns_422_and_no_duplicates(auth_headers, fav_teachers):
    """
    Test adding the same teacher twice returns a 422 (or accepted safe code) 
    and does not create duplicates in the favorites list.

    This test validates that the API prevents duplication of favorite teachers:
      - The first `add` succeeds and places the teacher into the list.
      - The second attempt with the same `teacherId` responds with:
          * 422 Unprocessable Entity and `"isExists"` error message, OR
          * 200/201/204 (safe handling without duplication).
      - The favorites list contains exactly one instance of that teacher.

    Args:
        auth_headers (tuple): Fixture providing (headers, email) for an authenticated user.
        fav_teachers (fixture): Factory fixture returning a Client wrapper for the
                                FavoriteTeachers API.

    Steps:
        1. Clear the favorites list.
        2. Add teacher ID_B once.
        3. Try to add the same teacher again.
        4. Verify the response status code and message.
        5. Fetch the favorites list and check that there is only one entry for ID_B.

    Assertions:
        - The second add returns 422 or another allowed status (OK/Created/No Content).
        - The error message contains `"isExists"` if 422 is returned.
        - The teacher ID_B appears only once in the favorites list.

    Fails if:
        - The API allows duplicates.
        - The second add returns an unexpected status code.
    """
    headers, _ = auth_headers
    api = fav_teachers(headers)

    api.clear()
    api.add(ID_B)

    r = api.add_ignore_exists(ID_B)
    assert r.status_code in (
        HTTPStatus.OK,
        HTTPStatus.CREATED,
        HTTPStatus.NO_CONTENT,
        HTTPStatus.UNPROCESSABLE_ENTITY,
    )
    if r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        assert "isExists" in (r.text or "")

    ids = [t["id"] for t in (api.list() or [])]
    assert ids.count(ID_B) == 1, f"Expected no duplicates, got {ids}"


@pytest.mark.favorite_teachers
def test_clear_helper_removes_all(auth_headers, fav_teachers):
    """
    Test that `clear()` helper successfully removes all teachers from favorites.

    This test verifies the utility function `clear()` in the fixture client:
      - After adding multiple teachers, invoking `clear()` should remove all entries.
      - Subsequent calls to `list()` must return an empty list.

    Args:
        auth_headers (tuple): Fixture providing (headers, email) for an authenticated user.
        fav_teachers (fixture): Factory fixture returning a Client wrapper for the
                                FavoriteTeachers API.

    Steps:
        1. Clear the favorites list to start with a clean state.
        2. Add two teacher IDs (ID_A and ID_B).
        3. Call `clear()` to remove all favorites.
        4. Verify the favorites list is empty.

    Assertions:
        - After clear(), `list()` returns an empty list.

    Fails if:
        - Teachers remain in the favorites list after clear().
    """
    headers, _ = auth_headers
    api = fav_teachers(headers)

    api.clear()
    for _id in (ID_A, ID_B):
        api.add(_id)

    api.clear()
    assert not api.list(), "clear() did not clean the list"


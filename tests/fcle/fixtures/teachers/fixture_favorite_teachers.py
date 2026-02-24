import pytest
from http import HTTPStatus
from settings import ENDPOINTS

@pytest.fixture
def fav_teachers(get_request, post_request, delete_request):
    base = ENDPOINTS['fav-teachers']  # "FavoriteTeachers"

    class Client:
        def __init__(self, headers):
            self.headers = headers

        # GET /api/FavoriteTeachers
        def list(self):
            r = get_request(base, headers=self.headers)
            assert r.status_code == HTTPStatus.OK, f"GET {base}: {r.status_code}, {r.text}"
            try:
                return r.json()
            except ValueError:
                import json
                return json.loads(r.text)

        # --- Строгий POST: допускает только 200/201/204
        def add(self, teacher_id: int):
            payload = {"teacherId": int(teacher_id)}
            r = post_request(payload, base, headers=self.headers)
            assert r.status_code in (HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.NO_CONTENT), \
                f"POST {base}: {r.status_code}, {r.text}"
            return r

        # --- Мягкий POST: игнорирует 422 favoriteTeacher.teacherId.isExists
        def add_ignore_exists(self, teacher_id: int):
            payload = {"teacherId": int(teacher_id)}
            r = post_request(payload, base, headers=self.headers)
            if r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY and "isExists" in (r.text or ""):
                return r
            assert r.status_code in (HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.NO_CONTENT), \
                f"POST {base}: {r.status_code}, {r.text}"
            return r

        def add_many(self, ids):
            for _id in ids:
                self.add(_id)

        # --- Строгий DELETE: допускает только 200/204
        def delete(self, teacher_id: int):
            endpoint = f"{base}/{int(teacher_id)}"
            r = delete_request(None, endpoint, headers=self.headers)
            assert r.status_code in (HTTPStatus.OK, HTTPStatus.NO_CONTENT), \
                f"DELETE {endpoint}: {r.status_code}, {r.text}"
            return r

        # --- Мягкий DELETE: игнорирует 422 favoriteTeacher.teacherId.notFound
        def delete_ignore_missing(self, teacher_id: int):
            endpoint = f"{base}/{int(teacher_id)}"
            r = delete_request(None, endpoint, headers=self.headers)
            if r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY and "notFound" in (r.text or ""):
                return r
            assert r.status_code in (HTTPStatus.OK, HTTPStatus.NO_CONTENT), \
                f"DELETE {endpoint}: {r.status_code}, {r.text}"
            return r

        def delete_many(self, ids):
            for _id in ids:
                self.delete(_id)

        def clear(self):
            current = self.list() or []
            ids = [t["id"] for t in current]
            for _id in ids:
                # сервер возвращает 422 при повторном удалении — используем мягкий вариант
                self.delete_ignore_missing(_id)

    def _factory(headers):
        return Client(headers)

    return _factory

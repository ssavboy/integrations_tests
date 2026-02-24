import pytest
from settings import ENDPOINTS

class UserLanguagesClient:
    def __init__(self, headers, get_request, post_request, delete_request):
        self.headers = headers
        self.get = get_request
        self.post = post_request
        self.delete_ = delete_request
        self.base = ENDPOINTS["user-languages"]

    def list(self):
        r = self.get(self.base, headers=self.headers)
        return r.json() if getattr(r, "ok", False) else []
    
    def get_lang(self, lang_id: int):
        r = self.get(f"{self.base}/{lang_id}", headers=self.headers)
        return r#.json() if getattr(r, "ok", False) else r.status_code

    def add(self, payload: dict):
        # Просто делаем POST, без assert
        return self.post(payload, self.base, headers=self.headers)

    def delete(self, lang_id: int):
        # delete_request тоже ждёт payload + endpoint
        return self.delete_(None, f"{self.base}/{lang_id}", headers=self.headers)


@pytest.fixture
def user_languages(auth_headers, get_request, post_request, delete_request):
    def _factory(headers=None):
        h = headers if isinstance(headers, dict) else (
            auth_headers[0] if isinstance(auth_headers, tuple) else auth_headers
        )
        return UserLanguagesClient(h, get_request, post_request, delete_request)
    return _factory

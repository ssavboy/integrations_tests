import pytest
import requests
from http import HTTPStatus

from utils.http_utils import request_options, request_put, request_post, variants, normalize_headers
from parametrs.parameters_update_user import generate_cases
from settings import ENDPOINTS


OK = HTTPStatus.OK
NO_CONTENT = HTTPStatus.NO_CONTENT
UNPROCESSABLE_ENTITY = HTTPStatus.UNPROCESSABLE_ENTITY
BAD_REQUEST = HTTPStatus.BAD_REQUEST


class UpdateUser:
    endpoint = ENDPOINTS["users"]

    def __init__(self, auth_headers, case):
        self.headers = normalize_headers(auth_headers)
        self.case = case
        self.attempts = []
        self.allow_map = {}

    def update(self):
        """
        Инкапсулирует всю логику обновления пользователя.
        """
        payload = self.case.to_payload()

        # OPTIONS
        for url in variants(self.endpoint):
            try:
                resp = request_options(url, headers=self.headers)
                self.allow_map[url] = resp.headers.get("Allow", "")
                self.attempts.append(("OPTIONS", url, resp.status_code, self.allow_map[url]))
            except Exception as e:
                self.attempts.append(("OPTIONS", url, f"EXC:{type(e).__name__}", str(e)))

        # PUT
        last = None
        for url in variants(self.endpoint):
            r = request_put(url, payload, headers=self.headers)
            self.attempts.append(("PUT", url, r.status_code, getattr(r, "text", "")))
            last = r
            if r.status_code not in (404, 405):
                return r

        # POST + Override
        if last is None or last.status_code in (404, 405):
            for url in variants(self.endpoint):
                r = request_post(url, payload, headers=self.headers, override="PUT")
                self.attempts.append(("POST+Override", url, r.status_code, getattr(r, "text", "")))
                if r.status_code not in (404, 405):
                    return r

        return last


@pytest.fixture
def update_user(auth_headers):
    def _make(case):
        return UpdateUser(auth_headers, case)
    return _make


@pytest.fixture(params=generate_cases(), ids=lambda case: case.label)
def update_user_case(request):
    return request.param

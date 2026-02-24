import pytest

from conftest import (
    post_request,
    get_request,
    put_request,
    delete_request,
    auth_headers
)
from settings import ENDPOINTS, OK

from .fixture_learning_materials_fetch_cases import (
    valid_fetch_payload,
    invalid_fetch_payload,
    response_keys_fetch
)
from .fixture_learning_materials_recent_cases import (
    valid_recent_payload,
    invalid_recent_payload,
    response_keys_recent
)
from .fixture_learning_materials_cases import (
    valid_payload,
    invalid_payload,
    response_keys,
    MaterialTypeData
)


@pytest.fixture
def learning_materials(auth_headers, get_request, post_request, put_request, delete_request):
    return LearningMaterialsClient(auth_headers[0], get_request, post_request, put_request, delete_request)


@pytest.fixture
def payload():
    def _payload(
            endpoint="",    # "", "fetch", "recent"
            valid=True,     # valid if True; invalid otherwise
            case=""         # 
            ):
        
        if endpoint == "fetch":
            return (valid_fetch_payload(case) if valid 
                    else invalid_fetch_payload(case))
        elif endpoint == "recent":
            return (valid_recent_payload(case) if valid 
                    else invalid_recent_payload(case))
        elif endpoint == "":
            return (valid_payload(case) if valid
                    else invalid_payload(case))

    return _payload


@pytest.fixture
def validate_structure():
    def _validate_structure(
            endpoint="", 
            data={}
            ):
        
        required = ()

        if endpoint == "fetch":
            required = response_keys_fetch
        elif endpoint == "recent":
            required = response_keys_recent
        elif endpoint == "":
            required = response_keys

        reciev_keys = data.keys()
        lost_keys = required - reciev_keys

        return lost_keys
    return _validate_structure


class LearningMaterialsClient:
    def __init__(self, auth_headers, get_request, post_request, put_request, delete_request):
        self.headers = auth_headers
        self.get_ = get_request
        self.post_ = post_request
        self.put_ = put_request
        self.delete_ = delete_request
        self.base = ENDPOINTS["learning_materials"]

    def post_fetch(self, payload: dict):
        return self.post_(payload, f"{self.base}/fetch", self.headers)
    
    def post_recent(self, payload: dict):
        return self.post_(payload, f"{self.base}/recent", self.headers)
    
    def post(self, payload: dict):
        return self.post_(payload, self.base, self.headers)
    
    def get(self, params):
        return self.get_(self.base, params, self.headers)
    
    def get_by_id(self, id_):
        return self.get_(f"{self.base}/{id_}", self.headers)
    
    def get_tags(self, params):
        return self.get_(f"{self.base}/tags", params, self.headers)

    def put(self, payload, id_,):
        return self.put_(payload, f"{self.base}/{id_}", self.headers)

    def delete(self, id_):
        return self.delete_(None, f"{self.base}/{id_}", self.headers)
    
    def delete_picture(self, id_):
        return self.delete_(None, f"{self.base}/picture/{id_}", self.headers)


@pytest.fixture
def add_material_and_get_id(learning_materials):
    def _add_material_and_get_id(
            case: str = "Random payload"
    ):  
        client = learning_materials

        try:
            payload_data = valid_payload(case)
        except KeyError as e:
            pytest.fail(f"{e}. Test case with this name does not exist.")
        
        response = client.post(
                                payload=payload_data
        )

        if response.status_code == OK:
            try:
                return payload_data, response.json()["id"]
            
            except KeyError as e:
                pytest.fail(f"{e}. Response is missing 'id' key")
        
        else:
            pytest.fail(
                f"Failed to execute POST request. "
                f"Status: {response.status_code}. "
                f"Response: {response.text}"
                )
    return _add_material_and_get_id
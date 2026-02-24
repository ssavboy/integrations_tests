import pytest

from settings import CONFLICT, BAD_REQUEST, OK
from fixtures.learning_materials.fixture_learning_materials import (
    learning_materials,
    payload, 
    validate_structure,
)


@pytest.mark.parametrize(
    ("validity_payload", "case", "expected_status_code"),
    (
        (True, "Random payload", (OK,)),
        (True, "Non-empty list response", (OK,)),
        (False, 'Invalid "pageSize"', (CONFLICT, BAD_REQUEST)),
        (False, 'Invalid "pageNumber"', (CONFLICT, BAD_REQUEST)),
        (False, 'Invalid "tags"', (CONFLICT, BAD_REQUEST)),
    )
)
@pytest.mark.learning_materials
class TestLearningMaterials:
    """
    Test suite for POST api/LearningMaterials/fetch endpoint.
    
    Tests learning materials retrieval with various payload scenarios
    including valid parameters and invalid pagination/tags cases.
    """

    @pytest.fixture(autouse=True)
    def setup(self, learning_materials):
        """
        AUTOUSED FIXTURE: Sets up test environment before each test method.
        
        Args:
            learning_materials: API client fixture for LearningMaterials endpoints
        """
        self.client = learning_materials


    def test_post_fetch_endpoint(
            self, 
            payload,
            validate_structure,
            validity_payload, 
            case, 
            expected_status_code
            ):
        """
        TEST: LearningMaterials/fetch with Various Payload Scenarios
        
        Verifies that:
        - API returns appropriate status codes for different payload cases
        - Valid payloads return 200 OK with properly structured list response
        - Invalid parameters are properly rejected with error status codes
        - Response data maintains expected schema structure
        
        Args:
            payload: Test payload generator fixture
            validity_payload: Boolean indicating payload validity
            case: Description of specific test scenario
            expected_status_code: Expected HTTP status code(s)
        """
        payload_data = payload(
                            endpoint="fetch",
                            valid=validity_payload, 
                            case=case
                            )

        response = self.client.post_fetch(payload_data)
        
        # Verify response status code matches expected value
        assert response.status_code in expected_status_code, (
            f"Expected {expected_status_code}, got {response.status_code}",
            f"{response.text}",
            f"{payload_data}"
        )

        # For successful responses (200 OK):
        # Validate response is a list
        if response.status_code == OK:
            data = response.json()

            assert isinstance(data, list), \
                f"Response data should be list, got {type(data)}"

            # If list is not empty, validate first item against expected schema
            if data != []:
                lost_keys = validate_structure(
                                            endpoint="fetch", 
                                            data=data[0]
                                            )
                
                assert len(lost_keys) == 0, \
                    f"Missing required keys: {lost_keys}"


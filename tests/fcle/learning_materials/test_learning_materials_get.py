import pytest
from random import randint

from settings import (
    OK, 
    CONFLICT, BAD_REQUEST
)

from fixtures.learning_materials.fixture_learning_materials import (
    learning_materials,
    add_material_and_get_id,
    payload,
)


@pytest.mark.learning_materials
class TestLearningMaterialsGet:
    """
    Test suite for GET api/LearningMaterials endpoints.
    
    Tests learning materials retrieval by ID and with various query parameters,
    including authorization requirements and pagination validation.
    """

    @pytest.fixture(autouse=True)
    def setup(self, learning_materials):
        """
        AUTOUSED FIXTURE: Sets up test environment before each test method.
        
        Args:
            learning_materials: API client fixture for LearningMaterials endpoints
        """
        self.client = learning_materials

    @pytest.mark.parametrize(
        ("authorization", ),
        (
            (True, ),
            (False, )
        )
    )
    def test_get_by_id(
            self, 
            add_material_and_get_id,
            authorization
            ):
        """
        TEST: Get Learning Material by ID with Authorization Check
        
        Verifies that:
        - API returns 200 OK for valid material ID requests
        - Both authorized and unauthorized access scenarios are handled
        
        Args:
            add_material_and_get_id: Fixture providing test material ID
            authorization: Boolean flag for authorization header presence
        """
        _, material_id = add_material_and_get_id()

        if not authorization:
            self.client.headers = {}

        response = self.client.get_by_id(material_id)

        assert response.status_code == OK, (
        f"{response.status_code}",
        f"{response.text}",    
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
    def test_get(
            self,
            payload,
            validity_payload,
            case,
            expected_status_code
    ):
        """
        TEST: Get Learning Materials List with Various Parameters
        
        Verifies that:
        - API handles valid and invalid pagination/tags parameters
        - Appropriate status codes are returned for different scenarios
        - Authorization requirements are enforced for list retrieval
        
        Args:
            payload: Test payload generator fixture
            validity_payload: Boolean indicating payload validity
            case: Description of specific test scenario
            expected_status_code: Expected HTTP status code(s)
        """
        params = payload(
                            endpoint="fetch",
                            valid=validity_payload, 
                            case=case
                            )

        response = self.client.get(params)
        
        assert response.status_code in expected_status_code, (
            f"Expected {expected_status_code}, got {response.status_code}",
            f"{response.text}",
            f"{params}"
        )
    
    @pytest.mark.parametrize(
        ("material_type", "tags_limit", "expected_status_code"),
        (
        # ============= Valid Params ============
            (randint(1, 3), randint(1, 10), (OK, )),
        # ============ Invalid Params ===========
            (1, 2**32, (CONFLICT, BAD_REQUEST)),    # max int for "limit"
            (2**32, 1, (CONFLICT, BAD_REQUEST)),    # max int for "materialType"
            (1, "tags", (CONFLICT, BAD_REQUEST)),   # invalid data type for "limit"
            ("type", 1, (CONFLICT, BAD_REQUEST))    # invalid data type for "materialType"
        )
    )
    def test_get_tags(
        self,
        material_type,
        tags_limit,
        expected_status_code
        ):
    
        params = {
            "materialType": material_type,
            "limit": tags_limit
        }
        response = self.client.get_tags(params)

        assert response.status_code in expected_status_code, (
            f"Expected {expected_status_code}, got {response.status_code}",
            f"{response.text}",
            f"{params}"
        )

        if response.status_code == OK:
            assert isinstance(response.json(), list)
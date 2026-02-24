import pytest

from settings import (
    OK, 
    UNAUTHORIZED, BAD_REQUEST, CONFLICT,
)

from fixtures.learning_materials.fixture_learning_materials import (
    learning_materials,
    payload,
    validate_structure
)


@pytest.mark.learning_materials
class TestLearningMaterialsPostPut:
    """
    Test suite for POST, PUT api/LearningMaterials endpoint.
    
    Tests learning materials creation and updates with different material types
    and authorization scenarios including unauthorized access attempts.
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
        ("validity_payload", "case", "expected_status_code"),
        (
            # ========== Valid Cases (with authorization) ==========
            (True, "materialType 1 with jpg", (OK,)),
            (True, "materialType 1 with png", (OK,)),
            (True, "materialType 2", (OK,)),
            (True, "materialType 3", (OK,)),
            
            # ========== Valid Cases (without authorization) ==========
            (True, "materialType 1 with jpg", (UNAUTHORIZED,)),
            
            # ========== Invalid Cases ==========
            (False, "Empty title", (BAD_REQUEST, CONFLICT)),
            (False, "Oversize title", (BAD_REQUEST, CONFLICT)),

            # Expected to fail due to API validation gaps
            pytest.param(
                False, "Invalid file format txt", (BAD_REQUEST, CONFLICT),
                marks=pytest.mark.xfail(reason="API currently doesn't validate invalid file format")
            ),
            pytest.param(
                False, "Zero target language", (BAD_REQUEST, CONFLICT),
                marks=pytest.mark.xfail(reason="API currently doesn't validate zero target language")
            ),
            pytest.param(
                False, "Zero written language", (BAD_REQUEST, CONFLICT),
                marks=pytest.mark.xfail(reason="API currently doesn't validate zero written language")
            ),
        )
    )
    def test_post_and_put(
        self, 
        payload,
        validate_structure,
        validity_payload, 
        case, 
        expected_status_code,
    ):
        """
        TEST: Create and Update Learning Material with Various Scenarios
        
        Verifies that:
        - API properly handles learning material creation for all material types
        - Authentication is required for successful material operations
        - Invalid payloads are properly rejected with appropriate error codes
        - Successfully created materials can be updated via PUT requests
        - Response structure matches expected schema for all material types
        - Material data persistence and field consistency across operations
        
        Args:
            payload: Test payload generator fixture
            validate_structure: Response schema validation fixture
            validity_payload: Boolean indicating payload validity
            case: Description of specific test scenario
            expected_status_code: Expected HTTP status code(s) for the test case
            
        Test Scenarios:
        - Valid material creation with different file types and material types
        - Unauthorized access attempts without proper authentication
        - Various invalid payload cases (empty title, oversize title, invalid formats)
        - Known API validation gaps (marked as expected failures)
        
        Steps:
        1. Generate payload based on test case parameters
        2. Clear authentication headers for unauthorized test cases
        3. Send POST request to create learning material
        4. Validate response status code matches expectations
        5. For successful creations:
           - Validate response structure against expected schema
           - Verify field consistency between request and response
           - Perform PUT request to update the created material
           - Validate update operation success
        """
        payload_data = payload(
                        endpoint="",
                        valid=validity_payload,
                        case=case
        )

        # Clear headers for unauthorized access testing
        if UNAUTHORIZED in expected_status_code:
            self.client.headers = {}

        response = self.client.post(
                                    payload=payload_data
                                )

        assert response.status_code in expected_status_code, (
        f"{response.status_code}",
        f"{response.text}",    
        )

        if response.status_code == OK:
            data = response.json()
            lost_keys = validate_structure(
                                        endpoint="", 
                                        data=data
                                        )
            
            assert len(lost_keys) == 0, \
                f"Missing required keys: {lost_keys}"
            
            assert data["title"] == payload_data["title"]
            assert data["description"] == payload_data["description"]
            assert data["content"] == payload_data["content"]

            # Test PUT request for successfully created data
            material_id = data["id"]
            payload_data["id"] = material_id
            response = self.client.put(
                                    payload=payload_data,
                                    id_=material_id
            )

            assert response.status_code == OK, (
                f"{payload_data}",
                f"{response.text}"
            )
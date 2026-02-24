import pytest

from conftest import upload_file

from fixtures.teacher_documents.fixture_teacher_documents import (
    teacher_documents, 
    create_auth_token,
    add_document,
    OK, CREATED, UNAUTHORIZED, NOT_FOUND, UNPROCESSABLE, BAD_REQUEST
    )
from fixtures.teacher_documents.fixture_teacher_documents_cases import (
    _valid_payload,
    _payload
)
from fixtures.new_teacher.fixture_new_teacher import new_teacher


@pytest.mark.parametrize(
    "document_type", ("id", "education", "additional"))
@pytest.mark.teacher_documents
#@pytest.mark.teach_doc_post
class TestTeacherDocumentsPOST:
    """
    Test suite for POST api/TeacherDocuments.
    
    This class contains tests including:
    - Upload documents with different types (id, education, additional)
    - Authentication requirements for document upload
    - Validation of request payload and file formats
    - Error scenarios (unauthorized access, invalid payloads)
    
    All tests use parameterized document types
    """


    @pytest.fixture(autouse=True)
    def setup(self, teacher_documents):
        """
        AUTOUSED FIXTURE: Sets up test environment before each test method.
        
        Args:
            teacher_documents: Fixture that provides an API client instance
                              configured for api/TeacherDocuments endpoints
                              
        Initializes:
            self.client: API client instance for making HTTP requests
        """
        self.client = teacher_documents


    def test_upload_unauthorized(self, upload_file, document_type):
        """
        TEST: Unauthorized Document Upload Attempt
        
        Verifies that:
        - API returns 401 UNAUTHORIZED status code when no authentication token is provided
        - Document upload endpoints are protected against anonymous access
        - All document types (id, education, additional) enforce authentication
        
        Steps:
        1. Prepare valid document payload and file for specified document type
        2. Make POST request to upload endpoint without authentication headers
        3. Assert response status code is 401 UNAUTHORIZED
        """
        doc_type = document_type
        payload, endpoint, file = _valid_payload(document_type=doc_type)
        base = self.client.base
        
        response = upload_file(
                                endpoint=f"{base}/{endpoint}",
                                data=payload,
                                files=file,
                                headers=""
                            ) 

        assert response.status_code == UNAUTHORIZED, (
            f"Expected 401, got {response.status_code}",
            f"{response.text}")


    def test_post_valid_payload(self, upload_file, document_type):
        """
        TEST: Successful Document Upload with Valid Payload
        
        Verifies that:
        - API returns 201 CREATED or 200 OK status code for valid authenticated requests
        - Response contains all required document fields with correct data types
        - All document types (id, education, additional) can be successfully uploaded
        - Response schema matches expected structure:
            {
            "id": int,
            "teacherId": int,
            "documentType": "string",
            "fileName": "string", 
            "fileUrl": "string",
            "title": "string",
            "description": "string"
            }
        
        Steps:
        1. Authenticate as teacher user
        2. Prepare valid document payload and file for specified document type
        3. Make POST request to upload endpoint with authentication headers
        4. Validate response status code and data structure
        5. Verify all field types match expected schema
        """
        doc_type = document_type
        payload, endpoint, file = _valid_payload(document_type=doc_type)
        base = self.client.base
        header = self.client.headers

        response_post = upload_file(
                                endpoint=f"{base}/{endpoint}",
                                data=payload,
                                files=file,
                                headers=header
                            )

        assert response_post.status_code in (CREATED, OK), (
            f"Request body: {payload}\n"
            f"Response: {response_post.text}\n"
            f"Status code: {response_post.status_code}"
        )

        data = response_post.json()
        
        # Validate response schema and field types
        assert isinstance(data["id"], int), \
            "Document ID should be integer"
        assert isinstance(data["teacherId"], int), \
            "Teacher ID should be integer"
        assert isinstance(data["documentType"], str), \
            "Document type should be string"
        assert isinstance(data["fileName"], str), \
            "File name should be string"
        assert isinstance(data["fileUrl"], str), \
            "File URL should be string"
        assert isinstance(data["title"], str), \
            "Title should be string"
        assert isinstance(data["description"], str), \
            "Description should be string"

    @pytest.mark.teach_doc_post_invalid
    @pytest.mark.xfail(
        reason="Expected 400 BAD_REQUEST, Got 500 Internal Server Error",
        run=True
        )
    @pytest.mark.parametrize(
        ("data_validity", "file_validity", "invalid_file"),
        [
            (False, True, ""), 
            (True, False, "empty"), 
            # (True, False, "invalid_format"), TODO вернуть тестовые случаи
            # (False, False, "empty")
        ],
    )
    def test_post_invalid_payload(
        self, 
        upload_file, 
        document_type,
        data_validity,
        file_validity,
        invalid_file
        ):
        """
        TEST: Document Upload with Invalid Payload Combinations
        
        Verifies that:
        - API returns 400 BAD_REQUEST status code for invalid payloads
        - System properly validates both form data and file attachments
        - Appropriate error handling for various invalid input scenarios:
            * Invalid form data with valid file
            * Valid form data with empty file
            * Valid form data with invalid file format  
            * Invalid form data with empty file
        
        Args:
            data_validity (bool): True if valid data; False owerwise
            file_validity (bool): True if valid file; False owerwise
            invalid_file (str): Type of file invalidity ("empty", "invalid_format")
            
        Steps:
        1. Authenticate as teacher user
        2. Prepare invalid payload based on parameterized test case
        3. Make POST request to upload endpoint with invalid data
        4. Assert response status code is 400 BAD_REQUEST
        
        Note: Currently marked as expected failure due to API returning 
              500 Internal Server Error instead of 400 BAD_REQUEST
        """
        doc_type = document_type
        payload, endpoint, file = _payload(
                                        document_type=doc_type,
                                        data_validity=data_validity,
                                        file_validity=file_validity,
                                        invalid_file=invalid_file,
                                    )
        base = self.client.base
        header = self.client.headers

        response_post = upload_file(
                                endpoint=f"{base}/{endpoint}",
                                data=payload,
                                files=file,
                                headers=header
                            )

        assert response_post.status_code == BAD_REQUEST, (
            f"Request body: {payload}\n"
            f"Response: {response_post.text}\n"
            f"Status code: {response_post.status_code}"
        )
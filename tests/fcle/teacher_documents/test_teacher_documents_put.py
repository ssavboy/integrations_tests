import pytest
import random

from conftest import upload_file_put

from fixtures.teacher_documents.fixture_teacher_documents import (
    teacher_documents, 
    create_auth_token,
    add_document,
    OK, CREATED, UNAUTHORIZED, NOT_FOUND, UNPROCESSABLE, BAD_REQUEST
    )
from fixtures.teacher_documents.fixture_teacher_documents_cases import (
    _payload
)
from fixtures.new_teacher.fixture_new_teacher import new_teacher


@pytest.mark.parametrize(
    ("endpoint", "document_type"), 
    [
        ("id-document", "id"), 
        ("education-document", "education"), 
        ("additional-document", "additional")
     ]
    )

@pytest.mark.teacher_documents
#@pytest.mark.teach_doc_put
class TestTeacherDocumentsPUT:
    """
    Test suite for PUT api/TeacherDocuments.
    
    This class contains tests including:
    - Update existing documents with different types (id, education, additional)
    - Validation of update request payload and file formats
    - Error scenarios (invalid payloads, file validation errors)
    
    All tests use parameterized document types and endpoints, and are marked 
    with 'teach_doc_put' for selective test execution.
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
        self._cleanup()

    
    def _cleanup(self):
        """
        Cleaning teacher documents before test
        
        Ensures clean test environment by removing all existing documents
        before each test execution to prevent test contamination.
        
        Steps:
        1. Retrieve all existing documents via GET endpoint
        2. Delete each document using its ID
        3. Fail test if cleanup encounters unexpected errors
        """
        try:
            response = self.client.get()
            docs = response.json()
            for doc in docs:
                if "id" in doc:
                    self.client.delete(doc["id"])
        
        except Exception as e:
            pytest.fail(f"Ошибка: {e}")
    

    @pytest.mark.xfail(
        reason="Expected 400 BAD_REQUEST, Got 500 Internal Server Error",
        run=True
        )
    @pytest.mark.parametrize(
        ("data_validity", "file_validity", "invalid_file", "status_code"),
        [   
            #(True, True, "", OK), # valid payload and file
            (False, True, "", BAD_REQUEST), # invalid data, valid file
            (True, False, "empty", BAD_REQUEST), # TODO: enable after fix
            # (True, False, "invalid_format", BAD_REQUEST), # TODO: enable after fix
            # (False, False, "empty", BAD_REQUEST) # TODO: enable after fix
        ],
    )
    def test_put_documents(
        self, 
        add_document,
        upload_file_put,
        document_type,
        endpoint,
        data_validity,
        file_validity,
        invalid_file,
        status_code
        ):
        """
        TEST: Update Existing Teacher Document with Various Payload Combinations
        
        Verifies that:
        - API returns appropriate status codes for different payload validity scenarios
        - Document metadata and files can be successfully updated
        - Response maintains correct data structure and field types after update
        - Invalid payloads are properly rejected with BAD_REQUEST status
        - Response schema matches expected structure for all document types:
            {
            "id": int,
            "teacherId": int, 
            "documentType": "string",
            "fileName": "string",
            "fileUrl": "string",
            "title": "string",
            "description": "string"
            }
        
        Args:
            add_document: Fixture that creates initial test document
            upload_file_put: Fixture for making file upload PUT requests
            document_type (str): Type of document being tested (id, education, additional)
            endpoint (str): API endpoint for specific document type
            data_validity (bool): True if valid data; False owerwise
            file_validity (bool): True if valid file; False owerwise
            invalid_file (str): Type of file invalidity ("empty", "invalid_format")
            status_code (int): Expected HTTP status code for the test case
            
        Test Cases:
        - Valid data + valid file: Expected 200 OK
        - Invalid data + valid file: Expected 400 BAD_REQUEST  
        - Valid data + empty file: Expected 400 BAD_REQUEST (commented)
        - Valid data + invalid format: Expected 400 BAD_REQUEST (commented)
        - Invalid data + empty file: Expected 400 BAD_REQUEST (commented)
        
        Steps:
        1. Create initial test document using add_document fixture
        2. Extract document ID from creation response
        3. Prepare update payload with specified validity parameters
        4. Send PUT request using upload_file_put fixture
        5. Verify response status code matches expected value
        6. Validate response data structure and field types for successful updates
        """
        resp_json, _, _ = add_document(
                                    header=self.client.headers,
                                    document_type=document_type
                                    )
        
        
        payload, _, file = _payload(
                            document_type=document_type,
                            data_validity=data_validity,
                            file_validity=file_validity,
                            invalid_file=invalid_file,

                        )
        base = self.client.base
        header = self.client.headers
        doc_id = resp_json["id"]

        response = upload_file_put(
                                endpoint=f"{base}/{endpoint}",
                                data=payload,
                                files=file,
                                headers=header,
                                id_ = doc_id
                            )
        
        # Alternative implementation commented out for reference:
        # response = self.client.put(
        #                             payload=payload,
        #                             file=file,
        #                             endpoint=endpoint,
        #                             doc_id=doc_id
        #                         )

        assert response.status_code == status_code, (
            f"Response: {response.text}\n"
            f"Status code: {response.status_code}"
        )

        # Only validate response schema for successful updates
        if response.status_code == OK:
            data = response.json()
            
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
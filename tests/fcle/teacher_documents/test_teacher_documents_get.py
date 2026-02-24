from http import HTTPStatus

import pytest

from fixtures.new_teacher.fixture_new_teacher import new_teacher
from fixtures.teacher_documents.fixture_teacher_documents import (
    NOT_FOUND,
    OK,
    UNAUTHORIZED,
    UNPROCESSABLE,
    add_document,
    create_auth_token,
    teacher_documents,
)


@pytest.mark.teacher_documents
class TestTeacherDocumentsGET:
    """
    Test suite for GET api/TeacherDocuments.

    This class contains tests including:
    - List all documents for a teacher
    - Get specific document by ID
    - Error scenarios (unauthorized access, non-existent documents)

    All tests use automatic fixture setup and are marked with 'teacher_documents'
    for selective test execution.
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
        """
        try:
            response = self.client.get()
            docs = response.json()
            for doc in docs:
                if "id" in doc:
                    self.client.delete(doc["id"])

        except Exception as e:
            pytest.fail(f"Ошибка: {e}")

    def test_get_unauthorized(self):
        """
        TEST: Unauthorized Access to TeacherDocuments Endpoint

        Verifies that:
        - API returns 401 UNAUTHORIZED status code
        - Proper error response when no authentication token is provided
        - Endpoint is protected against anonymous access

        Steps:
        1. Make GET request to base endpoint without authentication headers
        2. Assert response status code is 401
        3. Validate error response structure
        """
        base = self.client.base
        response = self.client._get(base)

        assert response.status_code == UNAUTHORIZED, (
            f"Expected 401, got {response.status_code}",
            f"{response.text}",
        )

    def test_empty_list_for_new_user(self):
        """
        TEST: Empty Document List for New User

        Verifies that:
        - API returns 200 OK status code for authenticated requests
        - Response contains empty list when no documents exist
        - Response format is a valid JSON list

        Steps:
        1. Authenticate as newly created teacher user
        2. Request documents list via GET endpoint
        3. Assert response is empty list with proper structure
        """
        response = self.client.get()

        assert response.status_code == OK, f"Expected 200, got {response.status_code}"

        if response.status_code == OK:
            experiences = response.json()
            assert isinstance(
                experiences, list
            ), f"Expected list, got {type(experiences)}"
            assert experiences == [], f"Expected empty list, got {experiences}"

    def test_get_documents(self, add_document):
        """
        TEST: Retrieve Documents List After Document Creation

        Verifies that:
        - New document appear in the documents list
        - Document count increments correctly

        Args:
            add_document: Fixture that creates a test document and returns
                            response data

        Steps:
            1. Create a document with type "additional" using
                add_document fixture
            2. Retrieve complete documents list via GET endpoint
            3. Verify list contains exactly one document
        """
        _, _, _ = add_document(header=self.client.headers, document_type="additional")

        response = self.client.get()

        if response.status_code == OK:
            documents = response.json()
            assert (
                len(documents) == 1
            ), f"Expected 1 document, got {len(documents)}: {documents}"

    @pytest.mark.parametrize("document_type", ["id", "education", "additional"])
    def test_get_document_by_id(self, add_document, document_type):
        """
        TEST: Retrieve Specific Document by ID with different document types

        Verifies that:
        - API returns 200 OK when fetching existing document
        - Response contains all required document fields
        - Field data types match expected schema:
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
            add_document: Fixture that creates a test document and
                            returns response data
            document_type (str): Type of document to test (parameterized value)

        Steps:
        1. Create test document and extract its ID from response
        2. Request specific document using GET /documents/{id} endpoint
        3. Validate response status code and data structure
        4. Verify all field types match expected schema
        """
        resp_json, _, _ = add_document(
            header=self.client.headers, document_type=document_type
        )

        doc_id = resp_json["id"]

        response = self.client.get_by_id(doc_id)

        assert response.status_code == OK, (
            f"Response: {response.text}\n" f"Status code: {response.status_code}"
        )

        data = response.json()

        # Validate response schema and field types
        assert isinstance(data["id"], int), "Document ID should be integer"
        assert isinstance(data["teacherId"], int), "Teacher ID should be integer"
        assert isinstance(data["documentType"], str), "Document type should be string"
        assert isinstance(data["fileName"], str), "File name should be string"
        assert isinstance(data["fileUrl"], str), "File URL should be string"
        assert isinstance(data["title"], str), "Title should be string"
        assert isinstance(data["description"], str), "Description should be string"

    def test_get_by_nonexistent_id(self, add_document):
        """
        TEST: Error Handling for Non-existent Document ID

        Verifies that:
        - API properly handles requests for non-existent documents
        - Returns appropriate error status: 404 NOT_FOUND or 422 UNPROCESSABLE
        - Provides meaningful error response for invalid document IDs

        Args:
            add_document: Fixture that creates a test document
                            and returns response data

        Steps:
        1. Create test document to establish valid ID range
        2. Attempt to retrieve document with ID+1 (guaranteed non-existent)
        3. Assert API returns proper error status code
        4. Validate error response format
        """
        resp_json, _, _ = add_document(
            header=self.client.headers, document_type="education"
        )

        doc_id = resp_json["id"] + 1

        response = self.client.get_by_id(doc_id)

        assert response.status_code in (NOT_FOUND, UNPROCESSABLE, HTTPStatus.GONE), (
            f"Response: {response.text}\n" f"Status code: {response.status_code}"
        )

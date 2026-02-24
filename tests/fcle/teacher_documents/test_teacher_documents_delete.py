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


@pytest.mark.parametrize("document_type", ["id", "education", "additional"])
@pytest.mark.teacher_documents
class TestTeacherDocumentsDELETE:
    """
    Test suite for DELETE api/TeacherDocuments/{id}.

    This class contains tests for document deletion functionality including:
    - Successful document deletion by ID
    - Unauthorized access handling

    All tests use automatic fixture setup
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

    def test_delete_unauthorized(self, add_document, document_type):
        """
        TEST: Unauthorized Access to Document Deletion Endpoint

        Verifies that:
        - API returns 401 UNAUTHORIZED status code when no authentication token is provided
        - Document deletion endpoint is properly protected against anonymous access
        - Existing documents remain untouched after unauthorized deletion attempt

        Args:
            add_document: Fixture that creates a test document and returns response data

        Steps:
        1. Create a test document using add_document fixture
        2. Extract document ID from creation response
        3. Attempt to delete document without authentication headers
        4. Verify API returns 401 status code
        5. Confirm document still exists by attempting to retrieve it
        """
        # Create test document first
        resp_json, _, _ = add_document(
            header=self.client.headers, document_type=document_type
        )
        doc_id = resp_json["id"]

        # Store original headers and remove authorization for unauthorized attempt
        original_headers = self.client.headers
        self.client.headers = {}

        # Attempt unauthorized deletion
        response = self.client.delete(doc_id)

        # Restore headers for subsequent operations
        self.client.headers = original_headers

        assert response.status_code == UNAUTHORIZED, (
            f"Expected 401 UNAUTHORIZED, got {response.status_code}\n"
            f"Response: {response.text}"
        )

        # Verify document still exists after unauthorized deletion attempt
        get_response = self.client.get_by_id(doc_id)
        assert get_response.status_code == OK, (
            f"Document should still exist after unauthorized deletion attempt. "
            f"Got status: {get_response.status_code}"
        )

    def test_delete_by_id(self, add_document, document_type):
        """
        TEST: Successful Document Deletion by ID

        Verifies that:
        - API returns 200 OK status code for successful deletion
        - Document is completely removed from the system
        - Document no longer appears in documents list
        - Attempting to access deleted document returns appropriate error

        Args:
            add_document: Fixture that creates a test document and returns response data

        Steps:
        1. Create a test document using add_document fixture
        2. Extract document ID from creation response
        3. Delete the document using authenticated DELETE request
        4. Verify deletion returns 200 OK status
        5. Confirm document is removed from documents list
        6. Verify GET request for deleted document returns 404 NOT_FOUND or 422 UNPROCESSABLE
        """
        # Create test document
        resp_json, _, _ = add_document(
            header=self.client.headers, document_type=document_type
        )

        doc_id = resp_json["id"]

        # Delete the document
        response = self.client.delete(doc_id)

        assert response.status_code == OK, (
            f"Expected 200 OK for successful deletion, got {response.status_code}\n"
            f"Response: {response.text}"
        )

        # Verify document is removed from documents list
        list_response_after = self.client.get()
        docs_after = list_response_after.json()
        doc_ids_after = [doc["id"] for doc in docs_after]
        assert (
            doc_id not in doc_ids_after
        ), f"Document {doc_id} should not exist in documents list after deletion"

        # Verify document cannot be retrieved by ID
        get_response = self.client.get_by_id(doc_id)
        assert get_response.status_code in (
            NOT_FOUND,
            UNPROCESSABLE,
            HTTPStatus.GONE,
        ), (
            f"Expected 404 or 422 when accessing deleted document, got {get_response.status_code}\n"
            f"Response: {get_response.text}"
        )

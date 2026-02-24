import pytest

from conftest import upload_file
from fixtures.new_teacher.fixture_new_teacher import (
    OK,
    new_teacher,
    new_teacher_params,
    new_upload_params,
)
from settings import ENDPOINTS


@pytest.mark.new_teacher
class TestNewTeacher:
    token: None

    @staticmethod
    def test_new_teacher(new_teacher, new_teacher_params):
        """
        Tests the functionality of creating, updating, and retrieving teacher data using the NewTeacher class.

        This test verifies that:
        - A POST request creates a new teacher with valid teacherType and languageId.
        - A PUT request updates the teacher's teachingStyle and meAsTeacher fields.
        - A GET request retrieves the teacher data and ensures consistency with the previously set values.

        Args:
            new_teacher (NewTeacher): An instance of the NewTeacher class provided by the pytest fixture.

        Raises:
            AssertionError: If any of the response fields are empty or do not match expected values.
        """
        new_teacher = new_teacher(new_teacher_params)
        post_response, post_expected_status = new_teacher.post_new_teacher()
        TestNewTeacher.token = (
            new_teacher.token if post_response.status_code == OK else None
        )
        assert (
            post_response.status_code == post_expected_status
        ), f"Expected status code {post_expected_status}, but got {post_response.status_code}: {post_response.text}"
        if post_response.status_code == OK:
            teacher_type, lang_id = (
                post_response.json()["teacherType"],
                post_response.json()["languageId"],
            )
            assert teacher_type and lang_id is not None, f"Expected not empty value"

        if post_response.status_code == OK:
            put_response, put_expected_status = new_teacher.put_new_teacher()
            assert (
                put_response.status_code == put_expected_status
            ), f"Expected status code {put_expected_status}, but got {put_response.status_code}: {put_response.text}"

        if post_response.status_code == OK:
            get_response, get_expected_status = new_teacher.get_new_teacher()
            if get_response.status_code == get_expected_status:
                assert (
                    get_response.json()["teacherType"] == new_teacher.teacher_type
                ), f"Expected value {new_teacher.teacher_type}, but got {get_response['teacherType']}"
                assert (
                    get_response.json()["languageId"] == new_teacher.language_id
                ), f"Expected value {new_teacher.language_id}, but got {get_response['languageId']}"

                assert (
                    get_response.json()["teachingStyle"] == new_teacher.style_area
                ), f"Expected value {new_teacher.style_area}, but got {get_response.json()['teachingStyle']}"
                assert (
                    get_response.json()["meAsTeacher"] == new_teacher.as_teacher
                ), f"Expected value {new_teacher.as_teacher}, but got {get_response.json()['meAsTeacher']}"

    @staticmethod
    def test_upload_document(upload_file, new_upload_params):
        """
        Tests the document upload functionality by sending a file and associated metadata to a specified endpoint.

        Args:
            upload_file (callable): A function that handles the file upload request, accepting data, file, headers, and endpoint.
            new_upload_params (tuple): A tuple containing the parameters for the upload:
                - title (str): The title of the document.
                - description (str): The description of the document.
                - referenceid (str or None): An optional reference ID for the document.
                - file_name (str): The name of the file to be uploaded.
                - endpoint (str): The API endpoint to which the upload request is sent.
                - status_code (int): The expected HTTP status code for the response.

        Asserts:
            The response status code matches the expected `status_code`.

        Raises:
            AssertionError: If the response status code does not match the expected `status_code`.
            FileNotFoundError: If the specified file cannot be found or opened.
        """

        title, description, referenceid, file_name, endpoint, status_code = (
            new_upload_params
        )
        data = {
            "title": title,
            "description": description,
        }
        if TestNewTeacher.token is not None:
            headers = TestNewTeacher.token
            if referenceid is not None:
                data["referenceid"] = referenceid
            file = {
                "file": (
                    f"{file_name}",
                    open(f"tests/fcle/utils/example_files/{file_name}", "rb"),
                    "application/octet-stream",
                )
            }
            response = upload_file(data, file, headers, endpoint)
            assert (
                response.status_code == status_code
            ), f"Expected code {status_code}, but got {response.status_code}"

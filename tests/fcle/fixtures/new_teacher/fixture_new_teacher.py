import random
from http import HTTPStatus
from typing import Any, Callable, Tuple

import pytest
import requests

from conftest import auth_headers, get_request, post_request, put_request
from parametrs.parameters_new_teacher import ParametrsNewTeacher
from parametrs.parameters_upload_file import ParametrUploadFile
from settings import CONFLICT, ENDPOINTS

OK = HTTPStatus.OK
INTERNAL_SERVER_ERROR = HTTPStatus.INTERNAL_SERVER_ERROR


class NewTeacher:
    """
    A class to handle operations related to creating, updating, and retrieving new teacher data via API requests.

    Attributes:
        endpoint (str): The API endpoint for new teacher operations.
        language_id (list): List of available language IDs for random selection.
        token (str): Authentication token for API requests.
        email (str): Email associated with the teacher.
        request (Callable): Function to make POST requests.
        put_request (Callable): Function to make PUT requests.
        get_request (Callable): Function to make GET requests.
    """

    endpoint = ENDPOINTS["new_teacher"]

    def __init__(
        self,
        auth_headers,
        requests,
        params,
    ):
        """
        Initializes a NewTeacher instance with authentication and request functions.

        Args:
            token (str): Authentication token for API requests.
            email (str): Email associated with the teacher.
            post_request (Callable): Function to handle POST requests.
            put_request (Callable): Function to handle PUT requests.
            get_request (Callable): Function to handle GET requests.
        """
        self.token, self.email = auth_headers
        self.post_request, self.put_request, self.get_request = requests
        (
            self.teacher_type,
            self.language_id,
            self.style_area,
            self.as_teacher,
            self.status,
        ) = params

    def post_new_teacher(self) -> Tuple[str, Any]:
        """
        Sends a POST request to create a new teacher with a randomly selected language ID.

        Returns:
            Tuple[str, Any]: A tuple containing the response status and JSON data.

        Raises:
            pytest.fail: If the request fails due to a network or API error.
        """
        try:
            response = self.post_request(
                {
                    "teacherType": self.teacher_type,
                    "languageId": self.language_id,
                },
                self.endpoint,
                self.token,
            )
            return response, self.status
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Request failed: {e}")

    def put_new_teacher(self) -> Tuple[str, Any]:
        """
        Sends a PUT request to update teacher information with teaching style and description.

        Returns:
            Tuple[str, Any]: A tuple containing the response status and JSON data.

        Raises:
            pytest.fail: If the request fails due to a network or API error.
        """
        try:
            response = self.put_request(
                {
                    "teachingStyle": self.style_area,
                    "meAsTeacher": self.as_teacher,
                },
                self.endpoint,
                self.token,
            )
            return response, self.status
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Request failed: {e}")

    def get_new_teacher(self) -> Tuple[str, Any]:
        """
        Sends a GET request to retrieve information about a new teacher.

        Returns:
            Tuple[str, Any]: A tuple containing the response status and JSON data.

        Raises:
            pytest.fail: If the request fails due to a network or API error.
        """
        try:
            response = self.get_request(self.endpoint, headers=self.token)
            return response, self.status
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Request failed {e}")


@pytest.fixture
def new_teacher(auth_headers, post_request, put_request, get_request):
    """
    Pytest fixture to create a NewTeacher instance for testing.

    Args:
        auth_headers (Tuple[str, str]): A tuple containing the authentication token and email.
        post_request (Callable): Function to handle POST requests.
        put_request (Callable): Function to handle PUT requests.
        get_request (Callable): Function to handle GET requests.

    Returns:
        NewTeacher: An instance of the NewTeacher class initialized with the provided token, email,
                   and request functions.
    """

    def _add_validation(params):
        return NewTeacher(
            auth_headers,
            (post_request, put_request, get_request),
            params,
        )

    return _add_validation


# TODO: В будущем добавить больше негативных тестовых данных

teacher_params = [
    ParametrsNewTeacher.parametr_generation(status=OK),
    ParametrsNewTeacher.parametr_generation(valid_lang=False, status=CONFLICT),
    ParametrsNewTeacher.parametr_generation(valid_type=False, status=CONFLICT),
]

upload_params = [
    ParametrUploadFile.parameters_generation("id", OK),  # upload-id-document
    ParametrUploadFile.parameters_generation(
        "education", OK
    ),  # upload-education-document
    ParametrUploadFile.parameters_generation(
        "additional", OK
    ),  # upload-additional-document
]


@pytest.fixture(params=teacher_params)
def new_teacher_params(request):
    return request.param


@pytest.fixture(params=upload_params)
def new_upload_params(request):
    return request.param

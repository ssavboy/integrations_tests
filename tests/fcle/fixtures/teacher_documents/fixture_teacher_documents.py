import pytest
from http import HTTPStatus
from typing import BinaryIO

from settings import ENDPOINTS
from conftest import (
    upload_file_put,
    upload_file,
    get_request,
    delete_request
)

from parametrs.parameters_new_teacher import ParametrsNewTeacher
from fixtures.new_teacher.fixture_new_teacher import new_teacher
from fixtures.teacher_documents.fixture_teacher_documents_cases import (
    _valid_payload
)

# Successful status code
OK = HTTPStatus.OK
CREATED = HTTPStatus.CREATED

# Client Error Status Codes 
UNAUTHORIZED = HTTPStatus.UNAUTHORIZED
NOT_FOUND = HTTPStatus.NOT_FOUND
UNPROCESSABLE = HTTPStatus.UNPROCESSABLE_ENTITY
BAD_REQUEST = HTTPStatus.BAD_REQUEST


class TeacherDocuments:
    def __init__(
            self, 
            headers, 
            get_request, 
            upload_file, 
            delete_request, 
            upload_file_put
            ):
        
        self.headers = headers
        self._get = get_request
        self._upload = upload_file
        self._delete = delete_request
        self._put = upload_file_put
        self.base = ENDPOINTS["teacher_documents"]

    def get(self):
        return self._get(self.base, headers=self.headers)
    
    def get_by_id(self, doc_id: int):
        return self._get(f"{self.base}/{doc_id}", headers=self.headers)

    # def upload(
    #         self, 
    #         data: dict, 
    #         file: BinaryIO, 
    #         endpoint: str
    #         ):
    #     return self._upload(
    #                         data=data,
    #                         files=file,
    #                         headers=self.headers,
    #                         endpoint=f"{self.base}/{endpoint}",
    #                     ) 
    # TODO python вызывает фикстуру post_request вместо upload_file

    def delete(self, doc_id: int):
        return self._delete(None, f"{self.base}/{doc_id}", headers=self.headers)

    # def put(
    #         self, 
    #         payload: dict, 
    #         file: BinaryIO, 
    #         endpoint: str, 
    #         doc_id: int
    #         ):
    #     return self._put(
    #                     endpoint=f"{self.base}/{endpoint}",
    #                     data=payload,
    #                     files=file,
    #                     headers=self.headers,
    #                     id_ = doc_id
    #                     )
    # TODO python вызывает фикстуру put_request вместо upload_file_put


@pytest.fixture
def create_auth_token(new_teacher):
    """Фикстура для создания аутентификационного токена."""
    
    # Генерируем валидные параметры для создания учителя
    param = ParametrsNewTeacher.parametr_generation(status=HTTPStatus.OK)
    
    # Используем переданные параметры для создания учителя
    teacher_instance = new_teacher(param)
    
    # Выполняем POST-запрос для создания учителя и получения токена
    post_response, _ = teacher_instance.post_new_teacher()
    
    # Извлекаем токен из ответа, если статус успешный
    return teacher_instance.token if post_response.status_code == OK else None


@pytest.fixture
def teacher_documents(create_auth_token, get_request, post_request, delete_request, put_request):
    """Фикстура для создания объекта TeacherDocuments с готовым токеном."""

    return TeacherDocuments(create_auth_token, get_request, post_request, delete_request, put_request)


@pytest.fixture
def add_document(upload_file):
    """
    Фикстура для добавления валидных данных для TeacherDocuments

    Аргументы:
        document_type: "id", "education", "additional". 
            По умолчанию "id"
    """

    def _add_document(header, document_type):

        # Генерируем endpoint и data на основе передаваемого document_type
        data, endpoint, file = _valid_payload(document_type)
        
        base = ENDPOINTS["teacher_documents"]
        
        # Делаем запрос на сервер
        try:
            response = upload_file(
                                    data=data,
                                    files=file,
                                    headers=header,
                                    endpoint=f"{base}/{endpoint}"
                                )
            
            return response.json(), response.status_code, response.text
        
        except Exception as e:
            pytest.fail(f"Ошибка: {e}")
    
    return _add_document
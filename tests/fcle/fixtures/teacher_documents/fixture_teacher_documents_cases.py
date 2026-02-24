import pytest
import random


def _valid_payload(document_type):
    """
    Generate valid payload for document upload.
    
    Args:
        document_type (str): Type of document - "id", "education", "additional"
    
    Returns:
        tuple: (data, endpoint, file) for successful upload request
    """

    return _payload(
                    document_type=document_type,
                    data_validity=True,
                    file_validity=True,
                    invalid_file=""
                    )


def _payload(
        document_type :str,
        data_validity=True,
        file_validity=True,
        invalid_file=""
):
    """
    Generate payload for TeacherDocument API.
    
    Args:
        document_type (str): Type of document - "id", "education", "additional"
        data_validity: True if valid data; False owerwise
        file_validity: True if valid file; False owerwise
        invalid_file: Invalid cases - "empty", "invalid_format"
    
    Returns:
        tuple: (data, endpoint, file) for upload request
    """
    endpoint = _endpoint(document_type=document_type)
    
    data = _data(
                document_type=document_type,
                valid=data_validity
                )
    
    file = _read_file(_filename()) if file_validity \
            else _invalid_file(case=invalid_file)
    
    return data, endpoint, file


def _data(document_type, valid=True):
    """
    Create payload data based on document type requirements.
    
    Args:
        document_type (str): Type of document
        valid (bool): validity of data
    
    Returns:
        dict: valid data payload if valid is True; invalid data otherwise
    """
    data = {}
    
    if valid:
        data = {
            "title": "t" * 10,
            "description": "d" * 10,
        }
    
        if document_type == "education":
            data["referenceid"] = 1
    else:
        data = {
            "title": "t" * 101,
            "description": "d" * 101,
        }
        
        if document_type != "education":
            data["referenceid"] = 1
    
    return data


def _endpoint(document_type):
    """
    Get upload endpoint for specific document type.
    
    Args:
        document_type (str): Type of document
    
    Returns:
        str: API endpoint path for document upload
    """
    upload_endpoints = {
        "id": "upload-id-document",
        "education": "upload-education-document", 
        "additional": "upload-additional-document",
    }
    return upload_endpoints[document_type]


def _read_file(file_name):
    """
    Read file from filesystem and prepare for upload.
    
    Args:
        file_name (str): Name of file to read
    
    Returns:
        dict: File data formatted for multipart upload
    
    Raises:
        pytest.fail: If file cannot be found in any location
    """
    
    base_paths = [
        "tests/tests/fcle/utils/example_files/",
        "tests/fcle/utils/example_files/"
    ]
    
    for base_path in base_paths:
        try:
            file_path = f"{base_path}{file_name}"
            
            file = {
                "file": (
                    file_name,
                    open(file_path, "rb"),
                    "application/octet-stream",
                )
            }

            return file
        
        except FileNotFoundError:
            continue
    
    return pytest.fail("Не удалось открыть файл")
    

def _invalid_file(case="empty"):
    if case == "empty":
        return None
    if case == "invalid_format":
        return _read_file("blank.txt")


def _filename():
    """
    Generate random filename from allowed extensions.
    
    Returns:
        str: Random filename with pdf/png/jpg extension
    """
    return random.choice(["blank.pdf", "blank.png", "blank.jpg"])

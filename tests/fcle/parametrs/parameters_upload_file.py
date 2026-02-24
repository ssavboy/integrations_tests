import random

from settings import ENDPOINTS


class ParametrUploadFile:
    """
    Generates parameters for testing file upload functionality.

    Args:
        endpoint (str): The key to select the upload endpoint from the `upload_endpoints` dictionary
            (e.g., "id", "education", "additional").
        status_code (int): The expected HTTP status code for the upload response.
        valid_title (bool, optional): If True, generates a valid title ("valid title").
            If False, generates an invalid title ("aaa" repeated 10 times). Defaults to True.
        valid_description (bool, optional): If True, generates a valid description ("valid description").
            If False, generates an invalid description ("aaa" repeated 10 times). Defaults to True.
        valid_referenceid (bool, optional): If True, generates a valid reference ID (1).
            If False, generates an invalid reference ID (None). Defaults to True.
        valid_file_name (bool, optional): If True, generates a valid file name from ["blank.pdf", "blank.png", "blank.jpg"].
            If False, generates an invalid file name (empty string). Defaults to True.3

    Returns:
        tuple: A tuple containing:
            - title (str): The generated title for the upload.
            - description (str): The generated description for the upload.
            - referenceid (int or None): The generated reference ID.
            - file_name (str): The generated file name.
            - endpoint (str): The selected upload endpoint URL from `upload_endpoints`.
            - status_code (int): The expected HTTP status code.

    Example:
        >>> ParametrUploadFile.parameters_generation("id", 200)
        ('valid title', 'valid description', 1, 'blank.pdf', 'https://example.com/upload-id', 200)
        >>> ParametrUploadFile.parameters_generation("education", 400, valid_title=False)
        ('aaaaaaaaaa', 'valid description', 1, 'blank.png', 'https://example.com/upload-education', 400)

    Raises:
        KeyError: If the provided `endpoint` is not one of "id", "education", or "additional".
    """

    @staticmethod
    def parameters_generation(
        endpoint,
        status_code,
        valid_title=True,
        valid_description=True,
        valid_referenceid=True,
        valid_file_name=True,
    ):

        title = "valid title" if valid_title else "aaa" * 10
        description = "valid description" if valid_description else "aaa" * 10
        referenceid = 1 if valid_referenceid else None
        file_name = (
            random.choice(["blank.pdf", "blank.png", "blank.jpg"])
            if valid_file_name
            else ""
        )
        upload_endpoints = {
            "id": ENDPOINTS["upload-id-document"],
            "education": ENDPOINTS["upload-education-document"],
            "additional": ENDPOINTS["upload-additional-document"],
        }

        return (
            title,
            description,
            referenceid,
            file_name,
            upload_endpoints[endpoint],
            status_code,
        )

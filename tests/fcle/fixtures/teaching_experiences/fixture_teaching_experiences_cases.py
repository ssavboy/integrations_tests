import random

from datetime import datetime
from utils.fake_data_generators import generate_text
from jsonschema import validate, ValidationError


validation_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "teacherId": {"type": "number"},
        "organization": {"type": "string", "maxLength": 200},
        "position": {"type": "string", "maxLength": 100},
        "startYear": {"type": "number", "minimum": 1960},
        "finishYear": {"type": ["number", "null"]}, 
        "description": {"type": "string", "maxLength": 255},
        "createdAt": {"type": "string", "format": "date-time"},
        "updatedAt": {"type": "string", "format": "date-time"}
    },
    "required": ["id", "teacherId", "organization", "position", "startYear", "finishYear", "description", "createdAt", "updatedAt"],
    "additionalProperties": False
}


def _validate_response_jsonschema(server_response):
    """
    Валидирует ответ сервера по заданной схеме.
    Возвращает (is_valid, error_message)
    """
    try:
        validate(instance=server_response, schema=validation_schema)
        
        finish_year = server_response["finishYear"]
        if finish_year:
            start_year = server_response["startYear"]
            if finish_year < start_year:
                return False, f"Ошибка валидации: {ValidationError.message}"
        
        return True, "Валидация успешна."
        
    except ValidationError as e:
        return False, f"Ошибка валидации: {e.message}"


def _valid_payload():
    """
    Генерирует валидный payload для POST-запроса api/TeachingExperiences.
    """
    start_year = random.randint(1960, _cur_year())
    finish_year = _generate_finish_year(start_year)
    organization = _generate_text(5, 200)
    position = _generate_text(5, 100)
    
    return {
        "organization": organization,
        "position": position,
        "startYear": start_year,
        "finishYear": finish_year,
        "description": ""
    }


def _invalid_payload():
    """
    Генерирует невалидный payload для POST-запроса api/TeachingExperiences.
    """
    start_year = random.randint(-100, 1960)
    finish_year = _generate_invalid_finish_year()
    organization = _generate_invalid_organization()
    position = _generate_invalid_position()
    
    return {
        "organization": organization,
        "position": position,
        "startYear": start_year,
        "finishYear": finish_year,
        "description": ""
    }


def _cur_year():
    """Возвращает текущий год."""
    return datetime.now().year


def _generate_text(min_len=5, max_len=255):
    """Генерирует текст заданной длины."""
    return generate_text(length=random.randint(min_len, max_len))


def _generate_invalid_text(min_len=201, max_len=202):
    """Генерирует невалидный текст."""
    return _generate_text(min_len, max_len) if random.choice([True, False]) else "Aa"


def _generate_finish_year(start_year):
    """Генерирует валидный finishYear или None."""
    if random.choice([True, False]):
        return random.randint(start_year, _cur_year())
    return None


def _generate_invalid_finish_year():
    """Генерирует невалидный finishYear или None."""
    if random.choice([True, False]):
        return random.randint(_cur_year(), _cur_year() + 10)
    return None


def _generate_invalid_organization():
    """Генерирует невалидное значение для organization."""
    if random.choice([True, False]):
        return _generate_invalid_text(201, 202)
    return ""


def _generate_invalid_position():
    """Генерирует невалидное значение для position."""
    if random.choice([True, False]):
        return _generate_invalid_text(101, 102)
    return ""
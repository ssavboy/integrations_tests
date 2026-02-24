import pytest
import random
import base64
import mimetypes
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


def valid_payload(case):
    """
    Returns valid payload data for specified test case.
    
    Args:
        case: Test case identifier string
        
    Returns:
        Dictionary with valid payload data for material creation
    """
    cases = {
        "Random payload": MaterialTypeCases.random_payload,
        "materialType 1 with jpg": MaterialTypeCases.material_type1_jpg,
        "materialType 1 with png": MaterialTypeCases.material_type1_png,
        "materialType 2": MaterialTypeCases.material_type2,
        "materialType 3": MaterialTypeCases.material_type3,
    }

    data = cases[case]

    # Ensure material type 1 has picture data
    if data["materialType"] == 1 and data["picture"] == "":
        data["picture"] = image_to_data_url(random.choice(["blank.jpg", "blank.png"]))

    return data


def invalid_payload(case):
    """
    Returns invalid payload data for negative test cases.
    
    Args:
        case: Test case identifier string for invalid scenarios
        
    Returns:
        Dictionary with invalid payload data for error testing
    """
    cases = {
        "Empty title": MaterialTypeCases.empty_title,
        "Oversize title": MaterialTypeCases.oversize_title,
        "Zero target language": MaterialTypeCases.zero_target_language,
        "Zero written language": MaterialTypeCases.zero_written_language,
        "Invalid file format txt": MaterialTypeCases.invalid_file_format_txt,
    }

    data = cases[case]

    # Ensure material type 1 has picture data
    if data["materialType"] == 1 and data["picture"] == "":
        data["picture"] = image_to_data_url(random.choice(["blank.jpg", "blank.png"]))

    return data


# Expected keys in API response
response_keys = (
    "id", "userId", "title", "description", "targetLanguageId", 
    "writtenLanguageId", "categoryId", "tags", "content", "publishDate", 
    "updateDate", "picture", "parentId", "topParentId", "materialType", 
    "commentsCount", "isCommentsAllowed", "allowAiComment", "thumbnail", 
    "user", "childrens"
)


@dataclass
class MaterialTypeData:
    """
    Data class representing learning material structure.
    
    Provides default valid values for all required fields with
    random generation for ID fields to avoid conflicts.
    """
    title: str = "str"
    content: str = "str"
    targetLanguageId: int = field(default_factory=lambda: random.randint(1, 100))
    writtenLanguageId: int = field(default_factory=lambda: random.randint(1, 100))
    categoryId: int = field(default_factory=lambda: random.randint(1, 100))
    materialType: int = field(default_factory=lambda: random.randint(1, 3))
    description: str = ""
    tags: str = ""
    picture: str = ""
    parentId: Optional[int] = None
    topParentId: Optional[int] = None
    allowAiComment: bool = False
    commentsCount: int = 0
    isCommentsAllowed: bool = True
    user: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converts dataclass to dictionary for API payload."""
        return {
            "title": self.title,
            "description": self.description,
            "targetLanguageId": self.targetLanguageId,
            "writtenLanguageId": self.writtenLanguageId,
            "categoryId": self.categoryId,
            "tags": self.tags,
            "content": self.content,
            "picture": self.picture,
            "parentId": self.parentId,
            "topParentId": self.topParentId,
            "allowAiComment": self.allowAiComment,
            "materialType": self.materialType,
            "commentsCount": self.commentsCount,
            "isCommentsAllowed": self.isCommentsAllowed,
            "user": self.user
        }


def image_to_data_url(file_name):
    """
    Converts image file to base64 data URL.
    
    Searches for file in multiple paths and returns fallback 
    if file not found.
    
    Args:
        file_name: Name of the image file
        
    Returns:
        Base64 data URL string for the image
    """
    base_paths = [
        "tests/tests/fcle/utils/example_files/",
        "tests/fcle/utils/example_files/"
    ]

    for base_path in base_paths:
        try:
            file_path = f"{base_path}{file_name}"
            mime_type, _ = mimetypes.guess_type(file_path)

            with open(file_path, "rb") as image_file:
                base64_data = base64.b64encode(image_file.read()).decode('utf-8')
                data_url = f"data:{mime_type};base64,{base64_data}"
                return data_url
            
        except FileNotFoundError:
            continue

    # Return fallback blank image
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEU\
            AAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfD\
            wAChwGA60e6kgAAAABJRU5ErkJggg=="


@dataclass
class MaterialTypeCases:
    """
    Predefined test cases for learning material creation.
    
    Contains both valid and invalid payload examples for
    comprehensive API testing.
    """
    
    # ========== Valid Cases ==========
    random_payload = MaterialTypeData().to_dict()

    material_type1_jpg = MaterialTypeData(
        materialType=1,
        picture=image_to_data_url("blank.jpg")
    ).to_dict()
    
    material_type1_png = MaterialTypeData(
        materialType=1,
        picture=image_to_data_url("blank.png")
    ).to_dict()
    
    material_type2 = MaterialTypeData(
        materialType=2
    ).to_dict()
    
    material_type3 = MaterialTypeData(
        materialType=3
    ).to_dict()

    # ========= Invalid Cases =========
    empty_title = MaterialTypeData(
        title=""
    ).to_dict()

    oversize_title = MaterialTypeData(
        title=("s" * 201),
    ).to_dict()

    zero_target_language = MaterialTypeData(
        targetLanguageId=0
    ).to_dict()

    zero_written_language = MaterialTypeData(
        writtenLanguageId=0
    ).to_dict()

    invalid_file_format_txt = MaterialTypeData(
        picture=image_to_data_url("blank.txt")
    ).to_dict()
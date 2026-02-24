import random


"""
Параметры для API /LearningMaterials/fetch
"""

response_keys_fetch = (
    "id",
    "userId", 
    "title",
    "description",
    "targetLanguageId",
    "writtenLanguageId",
    "categoryId",
    "tags",
    "content",
    "publishDate",
    "updateDate",
    "picture",
    "parentId",
    "topParentId",
    "materialType",
    "commentsCount",
    "isCommentsAllowed",
    "allowAiComment",
    "thumbnail",
    "user",
    "childrens"
)


def valid_fetch_payload(case):
    
    cases = {
        "Random payload": {
            "byUserId": 0,
            "pageSize": random.randint(1, 100),
            "pageNumber": random.randint(1, 100),
            "languages": [],
            "materialType": random.randint(1, 3),
            "categoryId": random.randint(1, 100),
            "tags": tags(True)
        },
        # Hardtest for testing jsonschema current resources
        "Non-empty list response": {
            "byUserId": 1000000,
            "pageSize": 5,
            "pageNumber": 1,
            "languages": [],
            "materialType": 2,
            "categoryId": 0,
            "tags": ""
        },
    }

    return cases[case]
        
def invalid_fetch_payload(case):

    cases = {
        # Invalid "pageSize"
        'Invalid "pageSize"': {
            "byUserId": None,
            "pageSize": random.choice(
                    [
                        random.randint(-10, 0),
                        "str"
                    ]
                ),
            "pageNumber": random.randint(1, 100),
            "languages": [],
            "materialType": 0,
            "categoryId": 0,
            "tags": tags(True)
            },
        # Invalid "pageNumber"
        'Invalid "pageNumber"': {
            "byUserId": 0,
            "pageSize": random.randint(1, 100),
            "pageNumber": random.randint(-10, 0),
            "languages": [],
            "materialType": random.choice([1, 2, 3]),
            "categoryId": random.randint(1, 100),
            "tags": tags(True)
            },
        # Invalid "tags"
        'Invalid "tags"': {
            "byUserId": 0,
            "pageSize": random.randint(1, 100),
            "pageNumber": random.randint(1, 100),
            "languages": [],
            "materialType": random.choice([1, 2, 3]),
            "categoryId": random.randint(1, 100),
            "tags": tags(False)
            }
        }

    return cases[case]
        

def tags(valid):

    valid_tags = "A" * random.randint(1, 500)
    invalid_tags = ["A" * 501, 0]

    return valid_tags if valid else invalid_tags


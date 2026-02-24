import random

"""
Параметры для API /LearningMaterials/recent
"""

response_keys_recent = (
        "id",
        "title",
        "publishDate",
        "thumbnail",
        "url"
    )


def valid_recent_payload(case):
    
    cases = {
        # Hardtest for testing jsonschema current resources
        "Non-empty list response":
            { 
                "top": 10, 
                "materialType": 2
            },
        "Random payload":
            {
                "top": random.randint(1, 10),
                "materialType": random.randint(1, 3)
            }
    }

    return cases[case]
    
def invalid_recent_payload(case):
    cases = {
        '"top" less zero':
            { 
                "top": -1, 
                "materialType": random.randint(1, 3)
            },
        '"top" equal zero':
            { 
                "top": 0, 
                "materialType": random.randint(1, 3)
            },
        '"top" greater 100':
            { 
                "top": 101, 
                "materialType": random.randint(1, 3)
            },
    }

    return cases[case]
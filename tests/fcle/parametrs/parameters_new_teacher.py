import random
import re


class ParametrsNewTeacher:
    """
    Generates a random text string by combining words and optional characters.

    Args:
        words (list): A list of words to choose from for text generation.
        chars (list): A list of characters (punctuation or invalid characters) to optionally include.

    Returns:
        str: A randomly generated text string composed of words and optional characters, separated by spaces and stripped of trailing spaces.

    Example:
        >>> ParametrsNewTeacher.generate_text(["Hello", "World"], [".", "!"])
        'Hello ! World'
    """

    @staticmethod
    def generate_text(words, chars):
        result = []
        for _ in range(random.randint(3, 6)):
            result.append(random.choice(words))
            if random.random() > 0.5:
                result.append(random.choice(chars))
            result.append(" ")
        return "".join(result).strip()

    @staticmethod
    def parametr_generation(
        valid_type=True,
        valid_lang=True,
        valid_style=True,
        valid_about=True,
        status=None,
    ):
        text_area_map = {
            "words": ["Привет", "Мир", "Как", "дела", "Это", "тест", "Хорошо"],
            "punctuation": [".", ",", "!", "?", ";", ":", "-"],
            "invalid_chars": ["%", "$", "#", "@", "&"],
        }
        type = (
            random.choice(list(range(1, 60)))
            if valid_type
            else random.choice(["", None, random.randint(-3, 0)])
        )
        lang = (
            random.choice(list(range(1, 109)))
            if valid_lang
            else random.choice([random.randint(-3, 0), "", None])
        )
        style = (
            ParametrsNewTeacher.generate_text(
                text_area_map["words"], text_area_map["punctuation"]
            )
            if valid_style
            else ParametrsNewTeacher.generate_text(
                text_area_map["words"], text_area_map["invalid_chars"]
            )
        )
        about = (
            ParametrsNewTeacher.generate_text(
                text_area_map["words"], text_area_map["punctuation"]
            )
            if valid_about
            else ParametrsNewTeacher.generate_text(
                text_area_map["words"], text_area_map["invalid_chars"]
            )
        )
        return type, lang, style, about, status

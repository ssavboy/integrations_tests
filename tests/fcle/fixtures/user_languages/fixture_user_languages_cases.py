import random
from dataclasses import dataclass
from typing import Optional, Iterable, List, Dict
from fixtures.user_languages.fixture_user_languages import user_languages

import pytest


# ===== ВСПОМОГАТЕЛЬНОЕ =====
def _pick_free_language_id(used: Optional[Iterable[int]] = None,
                           pool: range = range(1, 51)) -> int:
    """Подбирает свободный languageId из указанного пула (по умолчанию 1..50)."""
    used_set = set(used or [])
    for lid in pool:
        if lid not in used_set:
            return lid
    # если вдруг всё занято — вернём что-нибудь из дальнего диапазона
    cand = random.randint(51, 200)
    while cand in used_set:
        cand = random.randint(51, 200)
    return cand


# ===== ГЕНЕРАТОР ВАЛИДНОГО PAYLOAD =====
def _valid_payload(*,
                   used_language_ids: Optional[Iterable[int]] = None,
                   language_id: Optional[int] = None,
                   is_target: Optional[bool] = None,
                   level: Optional[str] = None,
                   goal_id: Optional[int] = None,
                   subgoal_id: Optional[int] = None) -> Dict:
    """
    Генерирует валидный payload для POST /UserLanguages.
    Можно передать used_language_ids, чтобы исключить дубли по языкам.
    """
    final_is_target = is_target if is_target is not None else random.choice([True, False])
    final_language_id = language_id if language_id is not None else _pick_free_language_id(used_language_ids)
    final_level = level if level is not None else random.choice(["Native", "A1", "A2", "B1", "B2", "C1", "C2"])
    # goalId по правилам: >0, если isTarget=True; иначе 0
    final_goal_id = goal_id if goal_id is not None else (random.randint(1, 5) if final_is_target else 0)
    # subgoalId должен быть >0
    final_subgoal_id = subgoal_id if subgoal_id is not None else (random.randint(1, 5) if final_is_target else 0)

    return {
        "id": 0,  # на создании всегда 0
        "languageId": final_language_id,
        "isTarget": final_is_target,
        "level": final_level,
        "goalId": final_goal_id,
        "subgoalId": final_subgoal_id,
    }


# ===== НЕВАЛИДНЫЕ PAYLOAD-Ы ДЛЯ ТЕСТОВ =====
def _invalid_payloads() -> List[Dict]:
    """
    Список заведомо невалидных payload-ов (по валидатору).
    Важно: если сервер сейчас принимает какой-то из них, тест пометит это как xfail в самом тесте.
    """
    return [
        # languageId ≤ 0
        {"id": 0, "languageId": 0, "isTarget": False, "level": "A1", "goalId": 1, "subgoalId": 1},
        # isTarget = null
        {"id": 0, "languageId": 1, "isTarget": None, "level": "A1", "goalId": 1, "subgoalId": 1},
        # level вне допустимых значений
        {"id": 0, "languageId": 1, "isTarget": False, "level": "Z9", "goalId": 1, "subgoalId": 1},
        # isTarget=true без корректного goalId (>0)
        {"id": 0, "languageId": 1, "isTarget": True, "level": "B1", "goalId": 0, "subgoalId": 1},
        # subgoalId ≤ 0
        {"id": 0, "languageId": 1, "isTarget": False, "level": "A2", "goalId": 1, "subgoalId": 0},
    ]


# ===== СТАРЫЕ ШТУКИ (если где-то используются) =====
@dataclass(frozen=True)
class ULCase:
    name: str
    payload: dict
    kind: str  # "valid" | "invalid"
    xfail_reason: Optional[str] = None


def _all_cases():
    # оставил, если где-то нужна параметризация через готовые ULCase
    return [
        ULCase("valid-minimal", _valid_payload(is_target=False, level="", subgoal_id=1), "valid"),
        ULCase("valid-with-level", _valid_payload(level="B2"), "valid"),
        ULCase("valid-target-with-goal", _valid_payload(is_target=True, goal_id=5, subgoal_id=2), "valid"),

        ULCase("invalid-languageId<=0", {"id": 0, "languageId": 0, "isTarget": False, "level": "A1", "goalId": 1, "subgoalId": 1}, "invalid"),
        ULCase("invalid-isTarget-null", {"id": 0, "languageId": 1, "isTarget": None, "level": "A1", "goalId": 1, "subgoalId": 1}, "invalid"),
        ULCase("invalid-level-outside", {"id": 0, "languageId": 1, "isTarget": False, "level": "Z9", "goalId": 1, "subgoalId": 1}, "invalid"),
        ULCase("invalid-target-goalId=0", {"id": 0, "languageId": 1, "isTarget": True, "level": "B1", "goalId": 0, "subgoalId": 1}, "invalid",
               xfail_reason="Бэк принимает goalId=0 при isTarget=true (против валидатора)"),
        ULCase("invalid-subgoalId<=0", {"id": 0, "languageId": 1, "isTarget": False, "level": "A2", "goalId": 1, "subgoalId": 0}, "invalid"),
    ]


@pytest.fixture(params=_all_cases(), ids=lambda c: c.name)
def user_language_case(request) -> ULCase:
    return request.param

from dataclasses import dataclass
import random

from utils.fake_data_generators import (
    generate_bio,
    generate_city,
    generate_country,
    generate_first_name,
    generate_last_name,
    generate_nickname,
)

TG_ERR_SUBSTR = "TelegramAccount must be "  # делаем проверку по устойчивой подстроке

@dataclass
class UserUpdateCase:
    label: str
    nickname: object
    first_name: object
    last_name: object
    bio: object
    country: object
    city: object
    timezone: object
    expected_status: int | tuple
    telegram_account: str | None = None
    error_contains: str | None = None

    def to_payload(self):
        payload = {
            "nickname": self.nickname,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "bio": self.bio,
            "country": self.country,
            "city": self.city,
            "timezone": self.timezone,
        }
        if self.telegram_account is not None:
            payload["telegramAccount"] = self.telegram_account
        return payload

    def matches_expected(self, actual_status: int) -> bool:
        exp = self.expected_status
        if isinstance(exp, (tuple, list, set)):
            return actual_status in exp or (200 in exp and actual_status in (200, 204))
        if exp in (200, 204) and actual_status in (200, 204):
            return True
        if exp in (400, 409, 422) and actual_status in (400, 409, 422):
            return True
        return exp == actual_status


def generate_cases():
    # Таймзона от UTC-12 до UTC+14
    utc = random.randint(-12, 14)

    cases = [
        # ====== базовые кейсы ======
        UserUpdateCase(
            label="валидные данные",
            nickname=generate_nickname(),
            first_name=generate_first_name(),
            last_name=generate_last_name(),
            bio=generate_bio(),
            country=generate_country(),
            city=generate_city(),
            timezone=f"UTC{utc:+d}",
            expected_status=200,
        ),
        UserUpdateCase(
            label="пустая фамилия",
            nickname=generate_nickname(),
            first_name=generate_first_name(),
            last_name="",
            bio=generate_bio(),
            country=generate_country(),
            city=generate_city(),
            timezone=f"UTC{utc:+d}",
            expected_status=204,
        ),
        UserUpdateCase(
            label="пустое имя",
            nickname=generate_nickname(),
            first_name="",
            last_name=generate_last_name(),
            bio=generate_bio(),
            country=generate_country(),
            city=generate_city(),
            timezone=f"UTC{utc:+d}",
            expected_status=204,
        ),
        UserUpdateCase(
            label="bio слишком длинный",
            nickname=generate_nickname(),
            first_name=generate_first_name(),
            last_name=generate_last_name(),
            bio="C" * 600,
            country=generate_country(),
            city=generate_city(),
            timezone=f"UTC{utc:+d}",
            expected_status=422,
        ),
        UserUpdateCase(
            label="пустой nickname",
            nickname="",
            first_name=generate_first_name(),
            last_name=generate_last_name(),
            bio=generate_bio(),
            country=generate_country(),
            city=generate_city(),
            timezone=f"UTC{utc:+d}",
            expected_status=204,
        ),
        UserUpdateCase(
            label="country слишком длинный",
            nickname=generate_nickname(),
            first_name=generate_first_name(),
            last_name=generate_last_name(),
            bio=generate_bio(),
            country="C" * 60,
            city=generate_city(),
            timezone=f"UTC{utc:+d}",
            expected_status=422,
        ),

        # ====== Telegram — актуальное поведение бэка ======
        # валидные форматы
        UserUpdateCase("tg:@name",
                       generate_nickname(), generate_first_name(), generate_last_name(),
                       generate_bio(), generate_country(), generate_city(), f"UTC{utc:+d}",
                       expected_status=200, telegram_account="@eztetkrn"),
        UserUpdateCase("tg:name",
                       generate_nickname(), generate_first_name(), generate_last_name(),
                       generate_bio(), generate_country(), generate_city(), f"UTC{utc:+d}",
                       expected_status=200, telegram_account="eztetkrn"),
        # t.me-ссылки теперь принимает
        UserUpdateCase("tg:https t.me",
                       generate_nickname(), generate_first_name(), generate_last_name(),
                       generate_bio(), generate_country(), generate_city(), f"UTC{utc:+d}",
                       expected_status=200, telegram_account="https://t.me/eztetkrn"),
        UserUpdateCase("tg:http t.me",
                       generate_nickname(), generate_first_name(), generate_last_name(),
                       generate_bio(), generate_country(), generate_city(), f"UTC{utc:+d}",
                       expected_status=200, telegram_account="http://t.me/eztetkrn"),
        # telegram.me — пока не принимает (даёт 400) с новым текстом
        UserUpdateCase("tg:https telegram.me",
                       generate_nickname(), generate_first_name(), generate_last_name(),
                       generate_bio(), generate_country(), generate_city(), f"UTC{utc:+d}",
                       expected_status=400, telegram_account="https://telegram.me/eztetkrn",
                       error_contains=TG_ERR_SUBSTR),

        # явные невалидные примеры — теперь стабильный 400 с новым текстом
        UserUpdateCase("tg:пробелы",
                       generate_nickname(), generate_first_name(), generate_last_name(),
                       generate_bio(), generate_country(), generate_city(), f"UTC{utc:+d}",
                       expected_status=400, telegram_account="@user name",
                       error_contains=TG_ERR_SUBSTR),
        UserUpdateCase("tg:кириллица",
                       generate_nickname(), generate_first_name(), generate_last_name(),
                       generate_bio(), generate_country(), generate_city(), f"UTC{utc:+d}",
                       expected_status=400, telegram_account="@юзер",
                       error_contains=TG_ERR_SUBSTR),
        UserUpdateCase("tg:точка",
                       generate_nickname(), generate_first_name(), generate_last_name(),
                       generate_bio(), generate_country(), generate_city(), f"UTC{utc:+d}",
                       expected_status=400, telegram_account="user.name",
                       error_contains=TG_ERR_SUBSTR),
        UserUpdateCase("tg:пусто после t.me",
                       generate_nickname(), generate_first_name(), generate_last_name(),
                       generate_bio(), generate_country(), generate_city(), f"UTC{utc:+d}",
                       expected_status=400, telegram_account="https://t.me/",
                       error_contains=TG_ERR_SUBSTR),
        # пустая строка трактуется как очистка поля -> 200, без проверки текста
        UserUpdateCase("tg:пустая строка",
                       generate_nickname(), generate_first_name(), generate_last_name(),
                       generate_bio(), generate_country(), generate_city(), f"UTC{utc:+d}",
                       expected_status=200, telegram_account=""),
        UserUpdateCase("tg:лишние символы",
                       generate_nickname(), generate_first_name(), generate_last_name(),
                       generate_bio(), generate_country(), generate_city(), f"UTC{utc:+d}",
                       expected_status=400, telegram_account="@name@",
                       error_contains=TG_ERR_SUBSTR),

        # ====== Жёсткая валидация типов ======
        UserUpdateCase("firstName:int",
                       generate_nickname(), 123, generate_last_name(),
                       generate_bio(), generate_country(), generate_city(), f"UTC{utc:+d}",
                       expected_status=422),
        UserUpdateCase("lastName:obj",
                       generate_nickname(), generate_first_name(), {"x": 1},
                       generate_bio(), generate_country(), generate_city(), f"UTC{utc:+d}",
                       expected_status=422),
        UserUpdateCase("bio:float",
                       generate_nickname(), generate_first_name(), generate_last_name(),
                       3.14, generate_country(), generate_city(), f"UTC{utc:+d}",
                       expected_status=422),
        UserUpdateCase("country:list",
                       generate_nickname(), generate_first_name(), generate_last_name(),
                       generate_bio(), ["RU"], generate_city(), f"UTC{utc:+d}",
                       expected_status=422),
        UserUpdateCase("city:obj",
                       generate_nickname(), generate_first_name(), generate_last_name(),
                       generate_bio(), generate_country(), {"city": "Voronezh"}, f"UTC{utc:+d}",
                       expected_status=422),
        UserUpdateCase("timezone:list",
                       generate_nickname(), generate_first_name(), generate_last_name(),
                       generate_bio(), generate_country(), generate_city(), ["UTC"],
                       expected_status=422),
    ]

    return cases

import requests
from settings import BASE_URL


def build_url(endpoint: str) -> str:
    """Возвращает полный URL (если endpoint относительный)."""
    return endpoint if endpoint.startswith("http") else f"{BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"


def variants(url: str):
    """Возвращает варианты URL: без / и с /."""
    if not url:
        return []
    cleaned = url.rstrip("/")
    return [cleaned, f"{cleaned}/"]


def normalize_headers(headers):
    """Приводит headers к словарю (если передан список/tuple)."""
    return headers[0] if isinstance(headers, (list, tuple)) else headers


def request_options(url: str, headers=None):
    return requests.options(build_url(url), headers=headers, timeout=30)


def request_put(url: str, payload=None, headers=None):
    h = {"Content-Type": "application/json", "Accept": "application/json"}
    if headers:
        h.update(headers)
    return requests.put(build_url(url), json=payload, headers=h, timeout=30)


def request_post(url: str, payload=None, headers=None, override=None):
    h = {"Content-Type": "application/json", "Accept": "application/json"}
    if override:
        h["X-HTTP-Method-Override"] = override  # обход шлюзов, рубящих PUT
    if headers:
        h.update(headers)
    return requests.post(build_url(url), json=payload, headers=h, timeout=30)

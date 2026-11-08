"""api.py — загрузка курсов криптовалют с CoinGecko."""

import requests

API_URL = "https://api.coingecko.com/api/v3/coins/markets"
TIMEOUT = 15

class ApiError(Exception):
    """Ошибка получения данных от внешнего API."""

def fetch_rates(limit=50, currency="usd"):
    """Возвращает список монет с приведёнными к app.py ключами."""
    params = {
        "vs_currency": currency,
        "order": "market_cap_desc",
        "per_page": limit,
        "page": 1,
        "price_change_percentage": "24h",
    }
    try:
        resp = requests.get(
            API_URL,
            params=params,
            timeout=TIMEOUT,
            headers={"User-Agent": "CryptoRates/1.0"},
        )
    except requests.RequestException as exc:
        raise ApiError(f"Сетевая ошибка: {exc}") from exc

    if resp.status_code == 429:
        raise ApiError("Превышен лимит запросов (429). Подождите минуту.")
    if resp.status_code != 200:
        raise ApiError(f"HTTP {resp.status_code} от CoinGecko")

    try:
        data = resp.json()
    except ValueError as exc:
        raise ApiError("Некорректный JSON в ответе API") from exc

    if not isinstance(data, list):
        raise ApiError("Неожиданный формат ответа API")

    return [
        {
            "name": item.get("name"),
            "symbol": item.get("symbol"),
            "price": item.get("current_price"),
            "change_24h": item.get("price_change_percentage_24h"),
            "market_cap": item.get("market_cap"),
        }
        for item in data
    ]
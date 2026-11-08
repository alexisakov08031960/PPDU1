"""Работа с открытым API CoinGecko."""

import requests

API_URL = "https://api.coingecko.com/api/v3/coins/markets"
TIMEOUT = 10

COINS = [
    "bitcoin", "ethereum", "solana", "binancecoin", "ripple",
    "cardano", "dogecoin", "tron", "polkadot", "litecoin",
]

class ApiError(Exception):

def fetch_rates(coins=None):
    coins = coins or COINS
    params = {
        "vs_currency": "usd",
        "ids": ",".join(coins),
        "order": "market_cap_desc",
        "price_change_percentage": "24h",
    }
    try:
        response = requests.get(API_URL, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        raise ApiError("Превышено время ожидания ответа сервера")
    except requests.exceptions.ConnectionError:
        raise ApiError("Нет соединения с интернетом")
    except requests.exceptions.HTTPError as exc:
        code = exc.response.status_code
        if code == 429:
            raise ApiError("Слишком частые запросы (HTTP 429), подождите")
        raise ApiError(f"Ошибка сервера (HTTP {code})")
    except ValueError:
        raise ApiError("Некорректный ответ сервера")

    if not isinstance(data, list):
        raise ApiError("Неожиданный формат данных")

    return [
        {
            "name": item["name"],
            "symbol": item["symbol"].upper(),
            "price": item["current_price"],
            "change_24h": item.get("price_change_percentage_24h"),
            "market_cap": item.get("market_cap"),
        }
        for item in data
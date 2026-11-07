"""Функции для получения курсов криптовалют через CoinGecko."""

import json
import os
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_TOP = 50
API_BASE = "https://api.coingecko.com/api/v3"

def _api_key():
    """Ключ задаётся через переменную окружения, а не хранится в исходнике."""
    return os.environ.get("COINGECKO_API_KEY", "").strip()

def _get_json(endpoint, params=None):
    params = params or {}
    url = f"{API_BASE}/{endpoint}?{urllib.parse.urlencode(params)}"

    headers = {
        "Accept": "application/json",
        "User-Agent": "CryptoCrossRates/1.0",
    }

    key = _api_key()
    if key:
        headers["x-cg-demo-api-key"] = key

    request = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        if error.code == 401:
            raise RuntimeError(
                "CoinGecko отклонил API-ключ. Проверьте COINGECKO_API_KEY."
            ) from error
        if error.code == 429:
            raise RuntimeError(
                "CoinGecko ограничил частоту запросов. Подождите и попробуйте снова."
            ) from error
        raise RuntimeError(f"CoinGecko вернул HTTP {error.code}: {details}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Не удалось подключиться к CoinGecko: {error.reason}") from error
    except json.JSONDecodeError as error:
        raise RuntimeError("CoinGecko вернул ответ в неизвестном формате.") from error

def fetch_coin_list(limit=DEFAULT_TOP):
    """Возвращает список монет, отсортированный по рыночной капитализации."""
    limit = min(max(int(limit), 3), 250)
    per_page = min(limit, 250)

    data = _get_json(
        "coins/markets",
        {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": per_page,
            "page": 1,
            "sparkline": "false",
        },
    )

    return [
        {
            "id": coin["id"],
            "symbol": coin["symbol"].upper(),
            "name": coin["name"],
            "usd": float(coin["current_price"] or 0),
        }
        for coin in data
        if coin.get("id") and coin.get("current_price") is not None
    ][:limit]

def fetch_usd_prices(ids):
    """Возвращает текущие цены выбранных монет в долларах США."""
    coin_ids = [str(coin_id) for coin_id in ids]
    if not coin_ids:
        return {}

    data = _get_json(
        "simple/price",
        {
            "ids": ",".join(coin_ids),
            "vs_currencies": "usd",
        },
    )

    prices = {}
    for coin_id in coin_ids:
        try:
            prices[coin_id] = float(data[coin_id]["usd"])
        except (KeyError, TypeError, ValueError):
            raise RuntimeError(f"CoinGecko не вернул цену для монеты {coin_id}.")
    return prices

def fmt(value):
    """Форматирует число для отображения в таблице."""
    value = float(value)
    if value == 0:
        return "0"
    if abs(value) >= 1000:
        return f"{value:,.2f}"
    if abs(value) >= 1:
        return f"{value:.6f}".rstrip("0").rstrip(".")
    return f"{value:.10f}".rstrip("0").rstrip(".")
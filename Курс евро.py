import os
import sys

import requests
from requests.exceptions import JSONDecodeError, RequestException

BASE = os.getenv("FX_BASE_URL", "https://open.er-api.com")
VERSION = os.getenv("FX_API_VERSION", "v6")
CURRENCY = os.getenv("FX_BASE_CURRENCY", "USD").upper()
TARGET = os.getenv("FX_TARGET_CURRENCY", "RUB").upper()

url = f"{BASE.rstrip('/')}/{VERSION}/latest/{CURRENCY}"

def fetch_rates(url: str) -> dict:
    """Загружает курсы и возвращает словарь rates или бросает RuntimeError."""
    headers = {
        "Accept": "application/json",
        "User-Agent": "fx-checker/1.0",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=(3, 10))
        resp.raise_for_status()
    except RequestException as exc:
        raise RuntimeError(f"Сетевая ошибка при запросе {url}: {exc}") from exc

    try:
        data = resp.json()
    except (JSONDecodeError, ValueError) as exc:
        raise RuntimeError(
            f"Ответ не является JSON (HTTP {resp.status_code}): {resp.text[:200]!r}"
        ) from exc

    if data.get("result") != "success":
        raise RuntimeError(
            f"API вернул ошибку: {data.get('error-type', 'неизвестно')}"
        )

    if not isinstance(data.get("rates"), dict) or not data["rates"]:
        raise RuntimeError("В ответе отсутствует или пуст блок 'rates'")

    return data

def main() -> int:
    try:
        data = fetch_rates(url)
    except RuntimeError as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1

    base = data.get("base_code", CURRENCY)
    rates = data["rates"]

    if TARGET not in rates:
        print(
            f"Ошибка: в ответе нет валюты '{TARGET}'. "
            f"Всего валют: {len(rates)}",
            file=sys.stderr,
        )
        return 1

    updated = data.get("time_last_update_utc", "время неизвестно")

    print(f"1 {base} = {rates[TARGET]} {TARGET}")
    print(f"Обновлено: {updated}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
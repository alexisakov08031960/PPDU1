import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

# Кэш: ключ -> (timestamp, данные)
weather_cache: dict[tuple[float, float], tuple[float, dict]] = {}
CACHE_TTL = 600  # секунд

API_URL = "https://api.open-meteo.com/v1/forecast"

def _validate_coords(lat: float, lon: float) -> None:
    """Проверяет, что координаты — числа в допустимых пределах."""
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        raise TypeError("Широта и долгота должны быть числами")
    if not -90 <= lat <= 90:
        raise ValueError(f"Широта вне диапазона [-90, 90]: {lat}")
    if not -180 <= lon <= 180:
        raise ValueError(f"Долгота вне диапазона [-180, 180]: {lon}")

def get_weather(lat: float, lon: float, timeout: float = 5, use_cache: bool = True) -> Optional[dict]:
    """
    Возвращает текущую погоду по координатам.

    :param lat: широта (-90..90)
    :param lon: долгота (-180..180)
    :param timeout: таймаут запроса в секундах
    :param use_cache: использовать кэш (TTL — CACHE_TTL секунд)
    :return: dict с полями temperature, windspeed, winddirection, time — или None при ошибке
    """
    _validate_coords(lat, lon)

    key = (round(float(lat), 4), round(float(lon), 4))

    if use_cache:
        cached = weather_cache.get(key)
        if cached is not None:
            ts, payload = cached
            if time.time() - ts < CACHE_TTL:
                return payload

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,wind_speed_10m,wind_direction_10m",
        "wind_speed_unit": "kmh",
        "timezone": "auto",
    }
    headers = {"User-Agent": "weather-client/1.0"}

    try:
        response = requests.get(API_URL, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        data = response.json()
    except requests.Timeout:
        logger.warning("Превышено время ожидания запроса (%s с)", timeout)
        return None
    except requests.HTTPError as e:
        logger.warning("Сервер вернул ошибку: %s", e)
        return None
    except requests.RequestException as e:
        logger.warning("Сетевая ошибка: %s", e)
        return None
    except ValueError as e:  # включает JSONDecodeError
        logger.warning("Не удалось разобрать JSON: %s", e)
        return None

    current = data.get("current")
    if not isinstance(current, dict):
        reason = data.get("reason", "причина не указана")
        logger.warning("В ответе нет данных о погоде: %s", reason)
        return None

    weather = {
        "temperature": current.get("temperature_2m"),
        "windspeed": current.get("wind_speed_10m"),
        "winddirection": current.get("wind_direction_10m"),
        "time": current.get("time"),
    }

    if weather["temperature"] is None:
        logger.warning("В ответе отсутствует температура: %s", data)
        return None

    if use_cache:
        weather_cache[key] = (time.time(), weather)

    return weather

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    weather = get_weather(55.7558, 37.6173)  # Москва
    if weather:
        print(
            f"Температура: {weather['temperature']} °C, "
            f"ветер: {weather['windspeed']} км/ч, "
            f"направление: {weather['winddirection']}° "
            f"(на {weather['time']})"
        )
    else:
        print("Данные о погоде недоступны")
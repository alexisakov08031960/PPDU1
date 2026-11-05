import os
import webbrowser
from datetime import datetime, timedelta, timezone

import requests

from tkinter import *
from tkinter import messagebox

try:
    from opencage.geocoder import OpenCageGeocode
    OPENCAGE_AVAILABLE = True
except ImportError:
    OPENCAGE_AVAILABLE = False

# ============ ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ============

lat = None
lon = None
country = None
region = None
map_url = None

local_time_str = None      # строка "ЧЧ:ММ:СС"
timezone_name = None       # например "Europe/Moscow"
utc_offset = None          # например "+03:00"
local_dt_base = None       # datetime в местном поясе на момент запроса
local_anchor = None        # datetime.now() для отсчёта секунд

time_update_job = None     # id задачи автообновления
last_weather = None        # последние полученные данные о погоде

# ============ ПОГОДА + ВРЕМЯ (Open-Meteo) ============

def get_weather(lat, lon):
    """Возвращает текущую погоду и данные о часовом поясе по координатам."""
    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current_weather": "true",
                "current": "temperature_2m,wind_speed_10m",  # новый формат API
                "timezone": "auto",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        # Поддерживаем и старый (current_weather), и новый (current) формат ответа
        current_weather = data.get("current_weather")
        if not current_weather and data.get("current"):
            cur = data["current"]
            current_weather = {
                "temperature": cur.get("temperature_2m"),
                "windspeed": cur.get("wind_speed_10m"),
            }

        return {
            "weather": current_weather,
            "timezone": data.get("timezone"),
            "utc_offset_seconds": data.get("utc_offset_seconds"),
        }

    except Exception as e:
        return f"Ошибка при получении погоды: {e}"

def offset_to_str(seconds):
    """Преобразует смещение в секундах в строку вида '+03:00'."""
    if seconds is None:
        return None
    sign = "+" if seconds >= 0 else "-"
    seconds = abs(int(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes = remainder // 60
    return f"{sign}{hours:02d}:{minutes:02d}"

def format_time(dt):
    """Форматирует дату-время в читаемую строку."""
    months = [
        "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря",
    ]
    weekdays = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]
    return (
        f"{dt.strftime('%H:%M:%S')}, "
        f"{dt.day} {months[dt.month - 1]} {dt.year} "
        f"({weekdays[dt.weekday()]})"
    )

# ============ ПОИСК ГОРОДА ============

def get_coordinates(city, key=None):
    """Геокодирование города: OpenCage, при отсутствии ключа — Nominatim."""
    global lat, lon, country, region

    if OPENCAGE_AVAILABLE and key:
        try:
            geocoder = OpenCageGeocode(key)
            results = geocoder.geocode(city, language="ru")

            if results:
                lat = round(results[0]["geometry"]["lat"], 2)
                lon = round(results[0]["geometry"]["lng"], 2)

                components = results[0]["components"]
                country = components.get("country", "Страна не определена")
                region = components.get("state", "Регион не определен")

                return build_result_text()
            # Если OpenCage не нашёл — пробуем Nominatim ниже
        except Exception as e:
            # Ключ не авторизован (401) и т.п. — переходим на Nominatim
            print(f"OpenCage недоступен: {e}. Используем Nominatim.")

    # --- Резервный бесплатный геокодер ---
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": city, "format": "json", "limit": 1, "accept-language": "ru"},
            headers={"User-Agent": "city-coordinates-app/1.0"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        if not data:
            lat = lon = country = region = None
            return {"coordinates": "Город не найден", "map_url": None}

        item = data[0]
        lat = round(float(item["lat"]), 2)
        lon = round(float(item["lon"]), 2)

        parts = [p.strip() for p in str(item.get("display_name", "")).split(",") if p.strip()]
        country = parts[-1] if parts else "Страна не определена"
        region = parts[-2] if len(parts) >= 2 else "Регион не определен"

        return build_result_text()

    except Exception as e:
        lat = lon = country = region = None
        return {"coordinates": f"Ошибка: {e}", "map_url": None}

def build_result_text():
    """Собирает текст результата поиска и ссылку на карту."""
    osm_url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}"
    text = f"Широта: {lat}, Долгота: {lon}\nСтрана: {country}\nРегион: {region}"

    if local_dt_base is not None:
        text += f"\nЧасовой пояс: {timezone_name} (UTC{utc_offset})"
        text += f"\nМестное время: {local_time_str}"

    return {"coordinates": text, "map_url": osm_url}

def show_coordinates(event=None):
    """Поиск города и загрузка его погоды и местного времени."""
    global map_url, local_dt_base, local_anchor, local_time_str
    global timezone_name, utc_offset, time_update_job, last_weather

    city = entry.get().strip()
    if not city:
        label.config(text="Введите название города")
        return

    # Сначала гасим старый таймер, потом сбрасываем данные
    cancel_time_update()
    local_dt_base = None
    local_anchor = None
    local_time_str = None
    timezone_name = None
    utc_offset = None
    last_weather = None

    result = get_coordinates(city, key)
    map_url = result["map_url"]
    label.config(text=result["coordinates"])

    if lat is None or lon is None:
        return

    info = get_weather(lat, lon)

    if isinstance(info, str):
        label.config(text=result["coordinates"] + f"\n\n{info}")
        return

    last_weather = info["weather"]

    offset_seconds = info.get("utc_offset_seconds") or 0
    utc_offset = offset_to_str(offset_seconds)
    timezone_name = info.get("timezone") or "не определён"

    tz = timezone(timedelta(seconds=offset_seconds))
    local_dt_base = datetime.now(tz)
    local_anchor = datetime.now(timezone.utc)
    local_time_str = format_time(local_dt_base)

    refresh_label()
    schedule_time_update()

# ============ АВТООБНОВЛЕНИЕ ВРЕМЕНИ ============

def cancel_time_update():
    """Отменяет запланированное обновление времени."""
    global time_update_job
    if time_update_job is not None:
        try:
            window.after_cancel(time_update_job)
        except Exception:
            pass
        time_update_job = None

def schedule_time_update():
    """Планирует следующее обновление (без дублирования таймеров)."""
    global time_update_job
    cancel_time_update()
    time_update_job = window.after(1000, update_local_time)

def update_local_time():
    """Обновляет местное время на экране раз в секунду без запросов к API."""
    global local_time_str, time_update_job
    time_update_job = None

    # Окно могло быть закрыто — Winfo_exists бросит TclError
    try:
        if not window.winfo_exists():
            return
    except TclError:
        return

    if local_dt_base is None or local_anchor is None:
        return

    elapsed = datetime.now(timezone.utc) - local_anchor
    current_local = local_dt_base + elapsed
    local_time_str = format_time(current_local)

    refresh_label()
    schedule_time_update()

def refresh_label():
    """Перерисовывает подпись с актуальным временем."""
    if lat is None:
        return
    text = f"Широта: {lat}, Долгота: {lon}\nСтрана: {country}\nРегион: {region}"
    if timezone_name is not None:
        text += f"\nЧасовой пояс: {timezone_name} (UTC{utc_offset})"
        text += f"\nМестное время: {local_time_str}"
    label.config(text=text)

# ============ ПОГОДА (ОКНО) ============

def show_weather():
    """Открывает окно с текущей погодой."""
    if lat is None or lon is None:
        messagebox.showinfo(
            "Погода",
            "Сначала найдите город — нужны координаты.",
            parent=window,
        )
        return

    info = get_weather(lat, lon)
    weather_window = Toplevel(window)
    weather_window.title("Текущая погода")
    weather_window.geometry("340x170")

    if isinstance(info, str):
        Label(weather_window, text=info, wraplength=300).pack(pady=20)
        return

    current_weather = info["weather"]
    if not current_weather:
        Label(weather_window, text="Данные о погоде недоступны").pack(pady=20)
        return

    temperature = current_weather.get("temperature")
    windspeed = current_weather.get("windspeed")

    weather_text = (
        f"{country}, {region}\n\n"
        f"Температура: {temperature}°C\n"
        f"Скорость ветра: {windspeed} км/ч\n"
        f"Местное время: {local_time_str or '—'}"
    )
    Label(weather_window, text=weather_text).pack(pady=20)

# ============ СОХРАНЕНИЕ В ФАЙЛ ============

def save_to_file():
    """Сохраняет результаты поиска в search_results.txt рядом с программой."""
    if lat is None or lon is None:
        messagebox.showinfo(
            "Сохранение",
            "Нечего сохранять — сначала найдите город.",
            parent=window,
        )
        return

    city = entry.get().strip()

    lines = [
        "=" * 40,
        "РЕЗУЛЬТАТЫ ПОИСКА КООРДИНАТ",
        "=" * 40,
        f"Город: {city}",
        f"Широта: {lat}",
        f"Долгота: {lon}",
        f"Страна: {country}",
        f"Регион: {region}",
    ]

    if local_time_str is not None:
        lines.append(f"Часовой пояс: {timezone_name} (UTC{utc_offset})")
        lines.append(f"Местное время: {local_time_str}")

    if map_url:
        lines.append(f"Карта: {map_url}")

    lines.append(
        f"Запрос выполнен (UTC): "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}"
    )
    lines.append("")

    text = "\n".join(lines)

    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "search_results.txt")
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(text + "\n")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось записать файл:\n{e}", parent=window)
        return

    messagebox.showinfo("Сохранено", f"Результат записан в файл:\n{file_path}", parent=window)

# ============ КАРТА ============

def show_map():
    if map_url:
        webbrowser.open(map_url)
    else:
        messagebox.showinfo("Карта", "Сначала найдите город.", parent=window)

# ============ ИНТЕРФЕЙС ============

window = Tk()
window.title("Поиск координат города")
window.geometry("440x330")

# Ключ OpenCage: лучше брать из переменной окружения OPENCAGE_KEY
key = os.getenv("OPENCAGE_KEY", "97c595bec990457d975c12c16a4ec4a7")

entry = Entry(window, width=40)
entry.pack(pady=6)
entry.bind("<Return>", show_coordinates)

Button(window, text="Поиск", width=40, command=show_coordinates).pack(pady=2)
Button(window, text="Показать карту", width=40, command=show_map).pack(pady=2)
Button(window, text="Показать погоду", width=40, command=show_weather).pack(pady=2)
Button(window, text="Сохранить в файл", width=40, command=save_to_file).pack(pady=2)

label = Label(
    window,
    text="Введите город и нажмите Поиск",
    justify=LEFT,
    wraplength=400,
)
label.pack(pady=10)

window.mainloop()
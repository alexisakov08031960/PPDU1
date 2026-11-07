from opencage.geocoder import OpenCageGeocode, OpenCageGeocodeError
import pprint
from tkinter import *
from tkinter import messagebox
from translate import Translator
import webbrowser
import requests

try:
    translator = Translator(from_lang='en', to_lang='ru')
except Exception:
    translator = None

def tr(text):
    """Безопасный перевод: если либа недоступна — вернуть оригинал."""
    if not text:
        return '—'
    if translator is None:
        return text
    try:
        return translator.translate(text)
    except Exception:
        return text

def get_weather(lat, lon):
    """Возвращает dict или строку с текстом ошибки."""
    if lat is None or lon is None:
        return 'Сначала получите координаты города'
    try:
        response = requests.get(
            'https://api.open-meteo.com/v1/forecast',
            params={
                'latitude': lat,
                'longitude': lon,
                'current_weather': 'true',
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        if 'current_weather' not in data:
            return f"Ошибка при получении погоды: {data.get('reason', 'нет данных')}"
        return data['current_weather']
    except Exception as err:
        return f'Ошибка при получении погоды: {err}'

def show_weather():
    current_weather = get_weather(lat, lon)
    weather_window = Toplevel(root)
    weather_window.title('Текущая погода')
    weather_window.geometry('260x120+300+200')

    if isinstance(current_weather, str):
        text = current_weather
    else:
        # ВАЖНО: в новых версиях Open-Meteo ключи переименованы
        temperature = current_weather.get('temperature')
        windspeed = current_weather.get('windspeed',
                      current_weather.get('wind_speed_10m'))
        text = (f'Температура: {temperature} °С\n'
                f'Скорость ветра: {windspeed} км/ч')

    Label(weather_window, text=text, justify='left').pack(pady=10)

def get_coordinates(city, key):
    """Всегда возвращает dict: {'coordinates': str, 'map_url': str|None}."""
    global lat, lon
    lat = lon = None          # сбрасываем перед новым поиском - ключ к фиксу
    try:
        geocoder = OpenCageGeocode(key)
        results = geocoder.geocode(city)
        if not results:
            return {'coordinates': 'Город не найден', 'map_url': None}

        res = results[0]
        lat_full = res['geometry']['lat']
        lon_full = res['geometry']['lng']
        lat = round(lat_full, 2)
        lon = round(lon_full, 2)

        comp = res.get('components', {})
        country = tr(comp.get('country'))
        # state есть не у всех городов (Москва, Токио, Берлин...)
        region = tr(comp.get('state', comp.get('county', '—')))

        osm_url = f'https://www.openstreetmap.org/?mlat={lat_full}&mlon={lon_full}'
        return {
            'coordinates': (f'Широта: {lat_full}, Долгота: {lon_full}\n'
                            f'Страна: {country}\nРегион: {region}'),
            'map_url': osm_url,
        }
    except OpenCageGeocodeError as err:
        return {'coordinates': f'Ошибка геокодера: {err}', 'map_url': None}
    except Exception as err:
        return {'coordinates': f'Ошибка: {err}', 'map_url': None}

def show_coordinates(event=None):
    global map_url
    city = entry.get().strip()
    if not city:
        label['text'] = 'Введите город'
        return
    result = get_coordinates(city, key)
    label['text'] = result['coordinates']
    map_url = result['map_url']

def show_map(event=None):
    if map_url:
        webbrowser.open(map_url)
    else:
        messagebox.showinfo('Карта', 'Сначала получите координаты')

key = '96112fb6d80d4059ae9dabea94898600'
map_url = None
lat = None
lon = None

root = Tk()
root.title('Поиск координат города')
root.geometry('480x240')

frame1 = Frame(root)
frame1.pack()
frame2 = Frame(root)
frame2.pack(pady=(15, 0))

entry = Entry(frame1)
entry.pack(pady=(10, 0))
entry.bind('<Return>', show_coordinates)

label = Label(frame1, text='Введите город', justify='left')
label.pack()

Button(frame2, text='Получить координаты', command=show_coordinates).grid(row=0, column=0)
Button(frame2, text='Показать на карте', command=show_map).grid(row=0, column=1)
Button(frame2, text='Показать погоду', command=show_weather).grid(row=0, column=2)

root.mainloop()
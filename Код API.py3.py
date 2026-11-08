from tkinter import *
from opencage.geocoder import OpenCageGeocode
import webbrowser
import requests


def get_weather(lat, lon):
    try:
        response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true")
        weather_data = response.json()
        current_weather = weather_data['current_weather']
        return current_weather
    except Exception as e:
        return f"Ошибка при получении погоды: {e}"

def show_weather():
    current_weather = get_weather(lat, lon)  # lat и lon должны быть определены ранее
    weather_window = Toplevel(window)
    weather_window.title("Текущая погода")

    if isinstance(current_weather, str):
        label = Label(weather_window, text=current_weather)
    else:
        temperature = current_weather['temperature']
        windspeed = current_weather['windspeed']
        weather_text = f"Температура: {temperature}°C\nСкорость ветра: {windspeed} км/ч"
        label = Label(weather_window, text=weather_text)
        label.pack()

def get_coordinates(city, key):
    global lat, lon
    try:
        geocoder = OpenCageGeocode(key)
        results = geocoder.geocode(city, language='ru')

        if results:
            lat = round(results[0]['geometry']['lat'], 2)
            lon = round(results[0]['geometry']['lng'], 2)
            country = results[0]['components'].get('country', 'Страна не определена')
            region = results[0]['components'].get('state', 'Регион не определен')

            # Получаем URL для OpenStreetMap
            osm_url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}"



            return {
                "coordinates": f"Широта: {lat}, Долгота: {lon}\nСтрана: {country}\nРегион: {region}",
                "map_url": osm_url
            }
        else:
            return {"coordinates": "Город не найден", "map_url": None}
    except Exception as e:
        return {"coordinates": f"Ошибка: {e}", "map_url": None}

def show_coordinates(event=None):
    city = entry.get()
    result = get_coordinates(city, key)
    label.config(text=result["coordinates"])
    # Сохраняем URL в глобальной переменной для доступа из другой функции
    global map_url
    map_url = result["map_url"]

def show_map():
    if map_url:
        webbrowser.open(map_url)

# Интерфейс
window = Tk()
window.title("Поиск координат города")

key = '97c595bec990457d975c12c16a4ec4a7'
map_url = None

entry = Entry()
entry.pack()
entry.bind("<Return>", show_coordinates)

button = Button(text="Поиск", command=show_coordinates)
button.pack()

label = Label(text="Введите город и нажмите Поиск")
label.pack()

map_button = Button(text="Показать карту", command=show_map)
map_button.pack()


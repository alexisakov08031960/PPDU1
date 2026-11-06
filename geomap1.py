import os
import threading
import webbrowser

import requests
from tkinter import Tk, Frame, Entry, Label, Button, Toplevel, messagebox

from opencage.geocoder import OpenCageGeocode
from translate import Translator

OPENCAGE_KEY = os.environ.get("OPENCAGE_KEY", "96112fb6d80d4059ae9dabea94898600")
TIMEOUT = 10

translator = Translator(from_lang="en", to_lang="ru")
state = {"lat": None, "lon": None, "map_url": None, "title": ""}

def safe_translate(text, default="—"):
    if not text:
        return default
    try:
        return translator.translate(text)
    except Exception:
        return text          # перевод не критичен — не роняем логику

def get_weather(lat, lon):
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={"latitude": lat, "longitude": lon,
                    "current": "temperature_2m,wind_speed_10m"},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        cur = r.json().get("current")
        if not cur:
            return "Сервис погоды не вернул данные"
        return f"Температура: {cur['temperature_2m']} °С\n" \
               f"Скорость ветра: {cur['wind_speed_10m']} км/ч"
    except Exception as err:
        return f"Ошибка при получении погоды: {err}"

def get_coordinates(city):
    try:
        results = OpenCageGeocode(OPENCAGE_KEY).geocode(city)
        if not results:
            return "Город не найден", None
        geom = results[0]["geometry"]
        lat, lon = geom["lat"], geom["lng"]
        comps = results[0].get("components", {})
        state["lat"], state["lon"] = lat, lon
        state["title"] = results[0].get("formatted", city)
        text = (f"Широта: {lat}, Долгота: {lon}\n"
                f"Страна: {safe_translate(comps.get('country'))}\n"
                f"Регион: {safe_translate(comps.get('state') or comps.get('county'))}")
        url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=12/{lat}/{lon}"
        return text, url
    except Exception as err:
        return f"Ошибка геокодера: {err}", None

# --- сетевые вызовы вынесены из GUI-потока ---

def show_coordinates(event=None):
    city = entry.get().strip()
    if not city:
        label["text"] = "Введите город"
        return
    label["text"] = "Поиск…"
    btn["state"] = "disabled"

    def worker():
        text, url = get_coordinates(city)
        root.after(0, lambda: finish_coordinates(text, url))

    threading.Thread(target=worker, daemon=True).start()

def finish_coordinates(text, url):
    label["text"] = text
    state["map_url"] = url
    btn["state"] = "normal"

def show_weather():
    if state["lat"] is None or state["lon"] is None:
        messagebox.showwarning("Погода", "Сначала получите координаты города", parent=root)
        return
    weather_btn["state"] = "disabled"
    lat, lon, title = state["lat"], state["lon"], state["title"]

    def worker():
        text = get_weather(lat, lon)
        root.after(0, lambda: finish_weather(text, title))

    threading.Thread(target=worker, daemon=True).start()

def finish_weather(text, title):
    weather_btn["state"] = "normal"
    win = Toplevel(root)
    win.title("Текущая погода")
    win.geometry("380x260+380+280")
    win.resizable(False, False)
    Label(win, text=f"{title}\n\n{text}", justify="center",
          wraplength=250).pack(expand=True, padx=12, pady=12)
    
def show_map(event=None):
    if state["map_url"]:
        webbrowser.open(state["map_url"])
    else:
        messagebox.showinfo("Карта", "Сначала получите координаты города", parent=root)

root = Tk()
root.title("Поиск координат города")
root.geometry("500x270")
root.resizable(False, False)

frame1, frame2 = Frame(root), Frame(root)
frame1.pack()
frame2.pack(pady=(15, 0))

entry = Entry(frame1, width=40)
entry.pack(pady=(12, 0))
entry.bind("<Return>", show_coordinates)
entry.focus_set()

label = Label(frame1, text="Введите город", justify="center", wraplength=440)
label.pack(pady=(10, 0))

btn = Button(frame2, text="Получить координаты", command=show_coordinates)
btn.grid(row=0, column=0, padx=4)
map_btn = Button(frame2, text="Показать на карте", command=show_map)
map_btn.grid(row=0, column=1, padx=4)
weather_btn = Button(frame2, text="Показать погоду", command=show_weather)
weather_btn.grid(row=0, column=2, padx=4)

root.mainloop()
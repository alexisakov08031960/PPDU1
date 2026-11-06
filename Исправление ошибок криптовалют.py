import threading
import tkinter as tk
from tkinter import messagebox as mb
from tkinter import ttk

import requests

cryptocurrencies = {
    "bitcoin": "Биткоин (BTC)",
    "ethereum": "Эфириум (ETH)",
    "tether": "Tether (USDT)",
    "binancecoin": "BNB",
    "solana": "Solana (SOL)",
    "ripple": "XRP",
    "cardano": "Cardano (ADA)",
    "dogecoin": "Dogecoin (DOGE)",
    "toncoin": "Toncoin (TON)",
    "tron": "TRON (TRX)",
}

quote_currencies = {
    "usd": "Доллар США (USD)",
    "eur": "Евро (EUR)",
    "rub": "Российский рубль (RUB)",
}

API_URL = "https://api.coingecko.com/api/v3/simple/price"

def format_price(value: float) -> str:
    if value >= 1:
        return f"{value:,.2f}"
    return f"{value:.8f}".rstrip("0").rstrip(".")

def update_coin_label() -> None:
    code = coin_combobox.get()
    coin_label.config(text=cryptocurrencies.get(code, ""))

def update_quote_label() -> None:
    code = quote_combobox.get()
    quote_label.config(text=quote_currencies.get(code, ""))

def show_error(title: str, message: str) -> None:
    mb.showerror(title, message)
    result_label.config(text="")

def fetch_price() -> None:
    coin_id = coin_combobox.get().strip()
    quote = quote_combobox.get().strip()

    if not coin_id or not quote:
        mb.showwarning("Внимание", "Выберите криптовалюту и валюту котировки")
        return

    button.config(state=tk.DISABLED, text="Загрузка...")
    result_label.config(text="Запрос к API...")

    threading.Thread(
        target=request_price,
        args=(coin_id, quote),
        daemon=True,
    ).start()

def request_price(coin_id: str, quote: str) -> None:
    try:
        params = {
            "ids": coin_id,
            "vs_currencies": quote,
            "include_24hr_change": "true",
        }
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if coin_id not in data or quote not in data[coin_id]:
            root.after(
                0,
                show_error,
                "Ошибка",
                f"Данные для {coin_id} не найдены",
            )
            return

        price = data[coin_id][quote]
        change = data[coin_id].get(f"{quote}_24h_change")
        coin_name = cryptocurrencies.get(coin_id, coin_id)

        text = f"1 {coin_name} = {format_price(price)} {quote.upper()}"
        if change is not None:
            arrow = "▲" if change >= 0 else "▼"
            text += f"\nИзменение за 24 ч: {arrow} {change:+.2f} %"

        root.after(0, result_label.config, {"text": text})

    except requests.exceptions.Timeout:
        root.after(
            0,
            show_error,
            "Ошибка",
            "Превышено время ожидания ответа от сервера",
        )
    except requests.exceptions.RequestException as error:
        root.after(0, show_error, "Ошибка сети", str(error))
    except Exception as error:
        root.after(0, show_error, "Ошибка", str(error))
    finally:
        root.after(
            0,
            button.config,
            {"state": tk.NORMAL, "text": "Узнать курс"},
        )

root = tk.Tk()
root.title("Курсы криптовалют")
root.geometry("400x320")
root.resizable(False, False)

frame = ttk.Frame(root, padding=12)
frame.pack(fill=tk.BOTH, expand=True)

ttk.Label(frame, text="Криптовалюта").pack(anchor=tk.W)

coin_combobox = ttk.Combobox(
    frame,
    values=list(cryptocurrencies.keys()),
    state="readonly",
)
coin_combobox.pack(fill=tk.X, pady=(3, 0))
coin_combobox.bind("<<ComboboxSelected>>", lambda _event: update_coin_label())

coin_label = ttk.Label(frame, foreground="#555555")
coin_label.pack(anchor=tk.W, pady=(2, 8))

ttk.Label(frame, text="Валюта котировки").pack(anchor=tk.W)

quote_combobox = ttk.Combobox(
    frame,
    values=list(quote_currencies.keys()),
    state="readonly",
)
quote_combobox.pack(fill=tk.X, pady=(3, 0))
quote_combobox.bind("<<ComboboxSelected>>", lambda _event: update_quote_label())

quote_label = ttk.Label(frame, foreground="#555555")
quote_label.pack(anchor=tk.W, pady=(2, 8))

button = ttk.Button(frame, text="Узнать курс", command=fetch_price)
button.pack(fill=tk.X, pady=(4, 10))

result_label = ttk.Label(
    frame,
    text="Выберите пару и нажмите кнопку",
    justify=tk.LEFT,
    wraplength=360,
    font=("TkDefaultFont", 11, "bold"),
)
result_label.pack(anchor=tk.W)

coin_combobox.set("bitcoin")
update_coin_label()

quote_combobox.set("usd")
update_quote_label()

root.mainloop()
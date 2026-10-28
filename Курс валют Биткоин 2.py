import requests
from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb

BASE_CURRENCY = "BTC"

currencies = {
    "BTC": "Биткоин",
    "USD": "Доллар США",
    "EUR": "Евро",
    "CNY": "Юань",
    "RUB": "Российский рубль",
}

pop_curr = ['BTC', 'USD', 'EUR', 'RUB', 'CNY']

FIAT_URL = "https://open.er-api.com/v6/latest/{code}"
BTC_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"

def get_json(url):
    """Запрос с проверкой сети и JSON. Возвращает dict или None (уже показал ошибку)."""
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        mb.showerror('Ошибка сети', f'Не удалось получить курс:\n{e}')
    except ValueError:
        mb.showerror('Ошибка', 'Сервер вернул некорректный ответ')
    return None

def btc_to_usd():
    """Сколько долларов стоит 1 BTC."""
    data = get_json(BTC_URL)
    if data is None:
        return None
    try:
        return float(data['bitcoin']['usd'])
    except (KeyError, TypeError, ValueError):
        mb.showerror('Ошибка API', 'CoinGecko не вернул курс BTC')
        return None

def fiat_rates(base_code):
    """Словарь курсов: сколько единиц валюты в 1 единице base_code."""
    data = get_json(FIAT_URL.format(code=base_code.lower()))
    if data is None:
        return None
    if data.get('result') != 'success':
        mb.showerror('Ошибка API', str(data.get('error-type', 'неизвестная ошибка')))
        return None
    return data.get('rates', {})

def get_rate(base_code, target_code):
    """Курс 1 base_code -> target_code."""
    if base_code == "BTC" and target_code == "USD":
        return btc_to_usd()

    if base_code == "BTC":
        usd_price = btc_to_usd()
        if usd_price is None:
            return None
        rates = fiat_rates("USD")
        if rates is None:
            return None
        if target_code not in rates:
            mb.showerror('Ошибка', f'Валюта {target_code} не найдена')
            return None
        return usd_price * rates[target_code]

    rates = fiat_rates(base_code)
    if rates is None:
        return None
    if "USD" not in rates:
        mb.showerror('Ошибка', 'Нет курса к доллару')
        return None
    usd_value = rates["USD"]          # сколько USD в 1 base

    if target_code == "USD":
        return usd_value

    usd_rates = fiat_rates("USD")
    if usd_rates is None:
        return None
    if target_code not in usd_rates:
        mb.showerror('Ошибка', f'Валюта {target_code} не найдена')
        return None
    return usd_value * usd_rates[target_code]

def update_currency_label(event=None):
    code = target_combobox.get()
    currency_label.config(text=currencies.get(code, ""))

def exchange():
    target_code = target_combobox.get()
    base_code = base_combobox.get()

    if not target_code or not base_code:
        mb.showwarning('Внимание', 'Выберите базовую и целевую валюты')
        return

    if target_code == base_code:
        mb.showinfo('Курс обмена', f'Курс: 1 {base_code} = 1 {target_code}')
        return

    rate = get_rate(base_code, target_code)
    if rate is None:
        return

    base = currencies.get(base_code, base_code)
    target = currencies.get(target_code, target_code)

    fmt = ",.8f" if target_code == "BTC" else ",.4f"

    mb.showinfo(
        'Курс обмена',
        f'1 {base} ({base_code}) = {format(rate, fmt).rstrip("0").rstrip(".")} '
        f'{target} ({target_code})'
    )

root = Tk()
root.title("Курс валют")
root.geometry("360x260")

Label(root, text='Базовая валюта').pack(pady=(20, 5), padx=10)
base_combobox = ttk.Combobox(root, values=pop_curr, state="readonly")
base_combobox.pack()
base_combobox.current(pop_curr.index(BASE_CURRENCY))

Label(root, text='Целевая валюта').pack(pady=(15, 5), padx=10)
target_combobox = ttk.Combobox(root, values=pop_curr, state="readonly")
target_combobox.pack()
target_combobox.current(pop_curr.index("USD"))

currency_label = ttk.Label(root)
currency_label.pack(pady=10, padx=10)

button = Button(root, text='Получить курс', command=exchange)
button.pack(pady=5)

target_combobox.bind("<<ComboboxSelected>>", update_currency_label)
update_currency_label()

root.mainloop()
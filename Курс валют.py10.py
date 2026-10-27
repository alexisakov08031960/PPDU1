from tkinter import *
from tkinter import messagebox as mb
from tkinter import ttk

import requests

currencies = {
    'EUR': 'Евро',
    'JPY': 'Японская йена',
    'GBP': 'Фунт стерлингов',
    'AUD': 'Австралийский доллар',
    'CAD': 'Канадский доллар',
    'CHF': 'Швейцарский франк',
    'CNY': 'Китайский юань',
    'RUB': 'Российский рубль',
    'KZT': 'Казахстанский тенге',
    'UZS': 'Узбекский сум',
}

def update_currency_label(event=None):
    code = combobox.get()
    name = currencies.get(code, '')
    currency_label.config(text=name)

def exchange():
    code = combobox.get()

    if not code:
        mb.showwarning('Внимание', 'Выберите валюту из списка')
        return

    try:
        resp = requests.get('https://open.er-api.com/v6/latest/USD', timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if code not in data.get('rates', {}):
            mb.showerror('Ошибка', f'Валюта {code} не найдена в ответе сервиса')
            return

        exchange_rate = data['rates'][code]
        currency_name = currencies.get(code, code)

        mb.showinfo(
            'Курс обмена',
            f'{currency_name} ({code})\n'
            f'1 USD = {exchange_rate:.4f} {code}'
        )

    except requests.exceptions.RequestException as er:
        mb.showerror('Ошибка сети', str(er))
    except ValueError as er:
        mb.showerror('Ошибка', f'Некорректный ответ сервиса: {er}')
    except Exception as er:
        mb.showerror('Ошибка', str(er))

root = Tk()
root.title('Курс обмена валют USD')
root.geometry('380x220')

Label(root, text='Выберите валюту').pack(pady=10, padx=10)

popular_currencies = list(currencies.keys())

combobox = ttk.Combobox(root, values=popular_currencies, state='readonly')
combobox.pack(pady=10, padx=10)
combobox.bind('<<ComboboxSelected>>', update_currency_label)

currency_label = ttk.Label()
currency_label.pack()

Button(text='Получить курс обмена к доллару',
       command=exchange).pack(pady=10, padx=10)

root.mainloop()
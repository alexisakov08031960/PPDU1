import requests
from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb

currencies = {
    "USD": "Доллар США",
    "EUR": "Евро",
    "CNY": "Юань",
    "RUB": "Российский рубль",
}

pop_curr = ['EUR', 'USD', 'RUB', 'CNY']

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

    try:
        result = requests.get(
            f"https://open.er-api.com/v6/latest/{base_code}",
            timeout=10,
        )
        result.raise_for_status()
        data = result.json()
    except requests.RequestException as e:
        mb.showerror('Ошибка сети', f'Не удалось получить курс:\n{e}')
        return
    except ValueError:
        mb.showerror('Ошибка', 'Сервер вернул некорректный ответ')
        return

    if data.get('result') != 'success':
        mb.showerror('Ошибка API', data.get('error-type', 'неизвестная ошибка'))
        return

    rates = data.get('rates', {})
    if target_code not in rates:
        mb.showerror('Ошибка', f'Валюта {target_code} не найдена')
        return

    exchange_rate = rates[target_code]
    base = currencies.get(base_code, base_code)
    target = currencies.get(target_code, target_code)

    mb.showinfo(
        'Курс обмена',
        f'1 {base} ({base_code}) = {exchange_rate:.4f} {target} ({target_code})'
    )

root = Tk()
root.title("Курс валют")
root.geometry("360x260")

Label(root, text='Базовая валюта').pack(pady=(20, 5), padx=10)
base_combobox = ttk.Combobox(root, values=pop_curr, state="readonly")
base_combobox.pack()
base_combobox.current(1)

Label(root, text='Целевая валюта').pack(pady=(15, 5), padx=10)
target_combobox = ttk.Combobox(root, values=pop_curr, state="readonly")
target_combobox.pack()
target_combobox.current(0)

currency_label = ttk.Label(root)
currency_label.pack(pady=10, padx=10)

button = Button(root, text='Получить курс', command=exchange)
button.pack(pady=5)

target_combobox.bind("<<ComboboxSelected>>", update_currency_label)
update_currency_label()

root.mainloop()

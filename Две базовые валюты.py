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

def get_rate(base_code, target_code):
    """Возвращает курс base_code -> target_code или бросает исключение."""
    result = requests.get(
        f"https://open.er-api.com/v6/latest/{base_code}",
        timeout=10,
    )
    result.raise_for_status()
    data = result.json()

    if data.get('result') != 'success':
        raise RuntimeError(data.get('error-type', 'неизвестная ошибка'))

    rates = data.get('rates', {})
    if target_code not in rates:
        raise KeyError(target_code)

    return rates[target_code]

def exchange():
    target_code = target_combobox.get()
    base1_code = base_combobox.get()
    base2_code = base_combobox2.get()

    if not target_code or not base1_code or not base2_code:
        mb.showwarning('Внимание', 'Выберите обе базовые и целевую валюты')
        return

    bases = []
    for code in (base1_code, base2_code):
        if code not in bases:
            bases.append(code)

    target = currencies.get(target_code, target_code)
    lines = [f'Целевая валюта: {target} ({target_code})', '─' * 38]

    for base_code in bases:
        base = currencies.get(base_code, base_code)
        if base_code == target_code:
            lines.append(f'1 {base} ({base_code}) = 1 {target} ({target_code})')
            continue
        try:
            exchange_rate = get_rate(base_code, target_code)
        except requests.RequestException as e:
            lines.append(f'{base} ({base_code}): ошибка сети — {e}')
            continue
        except RuntimeError as e:
            lines.append(f'{base} ({base_code}): ошибка API — {e}')
            continue
        except KeyError:
            lines.append(f'{base} ({base_code}): валюта {target_code} не найдена')
            continue
        lines.append(f'1 {base} ({base_code}) = {exchange_rate:.4f} {target} ({target_code})')

    mb.showinfo('Курсы обмена', '\n'.join(lines))

root = Tk()
root.title("Курс валют")
root.geometry("380x340")

Label(root, text='Базовая валюта 1').pack(pady=(20, 5), padx=10)
base_combobox = ttk.Combobox(root, values=pop_curr, state="readonly")
base_combobox.pack()
base_combobox.current(1)

Label(root, text='Базовая валюта 2').pack(pady=(15, 5), padx=10)
base_combobox2 = ttk.Combobox(root, values=pop_curr, state="readonly")
base_combobox2.pack()
base_combobox2.current(0)

Label(root, text='Целевая валюта').pack(pady=(15, 5), padx=10)
target_combobox = ttk.Combobox(root, values=pop_curr, state="readonly")
target_combobox.pack()
target_combobox.current(2)

currency_label = ttk.Label(root)
currency_label.pack(pady=10, padx=10)

button = Button(root, text='Получить курс', command=exchange)
button.pack(pady=5)

target_combobox.bind("<<ComboboxSelected>>", update_currency_label)
update_currency_label()

root.mainloop()
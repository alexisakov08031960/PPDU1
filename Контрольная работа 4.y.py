from tkinter import *
from tkinter import messagebox as mb
from tkinter import ttk
import requests
import threading

cryptocurrencies = {
    'bitcoin': 'Биткоин (BTC)',
    'ethereum': 'Эфириум (ETH)',
    'tether': 'Tether (USDT)',
    'binancecoin': 'BNB',
    'solana': 'Solana (SOL)',
    'ripple': 'XRP',
    'cardano': 'Cardano (ADA)',
    'dogecoin': 'Dogecoin (DOGE)',
    'toncoin': 'Toncoin (TON)',
    'tron': 'TRON (TRX)',
}

quote_currencies = {
    'usd': 'Доллар США (USD)',
    'eur': 'Евро (EUR)',
    'rub': 'Российский рубль (RUB)',
}

API_URL = 'https://api.coingecko.com/api/v3/simple/price'

def format_price(value: float) -> str:
    """Красиво форматирует цену: крупные — с разделителями, мелкие — без округления в ноль."""
    if value >= 1:
        return f'{value:,.2f}'
    return f'{value:.8f}'.rstrip('0').rstrip('.')

def update_coin_label(event=None):
    code = coin_combobox.get()
    coin_label.config(text=cryptocurrencies.get(code, ''))

def update_quote_label(event=None):
    code = quote_combobox.get()
    quote_label.config(text=quote_currencies.get(code, ''))

def fetch_price():
    """Запрос к CoinGecko. Выполняется в отдельном потоке, чтобы окно не подвисало."""
    coin_id = coin_combobox.get().strip()
    quote = quote_combobox.get().strip()

    if not coin_id or not quote:
        mb.showwarning('Внимание', 'Выберите криптовалюту и валюту котировки')
        return

    button.config(state=DISABLED, text='Загрузка...')
    result_label.config(text='Запрос к API...')
    root.update_idletasks()

    try:
        params = {
            'ids': coin_id,
            'vs_currencies': quote,
            'include_24hr_change': 'true',
        }
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if coin_id not in data or quote not in data[coin_id]:
            mb.showerror('Ошибка', f'Данные для {coin_id} не найдены')
            result_label.config(text='')
            return

        price = data[coin_id][quote]
        change = data[coin_id].get(f'{quote}_24h_change')

        coin_name = cryptocurrencies[coin_id]
        quote_name = quote_currencies.get(quote, quote.upper())

        text = f'1 {coin_name} = {format_price(price)} {quote.upper()}'
        if change is not None:
            arrow = '▲' if change >= 0 else '▼'
            text += f'\nИзменение за 24 ч: {arrow} {change:+.2f} %'

        result_label.config(text=text)

    except requests.exceptions.Timeout:
        mb.showerror('Ошибка', 'Превышено время ожидания ответа от сервера')
        result_label.config(text='')
    except requests.exceptions.RequestException as er:
        mb.showerror('Ошибка сети', str(er))
        result_label.config(text='')
    except Exception as er:
        mb.showerror('Ошибка', er)
        result_label.config(text='')
    finally:
        button.config(state=NORMAL, text='Узнать курс')

def get_crypto_rate():
    threading.Thread(target=fetch_price, daemon=True).start()
root = Tk()
root.title('Курсы криптовалют')
root.geometry('400x320')
root.resizable(False, False)

frame = ttk.Frame(root, padding=12)
frame.pack(fill=BOTH, expand=True)

ttk.Label(frame, text='Криптовалюта').pack(anchor=W)
coin_combobox = ttk.Combobox(
    frame, values=list(cryptocurrencies.keys()), state='readonly'
)
coin_combobox.pack(fill=X, pady=(3, 0))
coin_combobox.bind('<<ComboboxSelected>>', update_coin_label)

coin_label = ttk.Label(frame, foreground='#555555')
coin_label.pack(anchor=W, pady=(2, 8))

ttk.Label(frame, text='Валюта котировки').pack(anchor=W)
quote_combobox = ttk.Combobox(
    frame, values=list(quote_currencies.keys()), state='readonly'
)
quote_combobox.pack(fill=X, pady=(3, 0))
quote_combobox.bind('<<ComboboxSelected>>', update_quote_label)

quote_label = ttk.Label(frame, foreground='#555555')
quote_label.pack(anchor=W, pady=(2, 8))

button = ttk.Button(frame, text='Узнать курс', command=get_crypto_rate)
button.pack(fill=X, pady=(4, 10))

result_label = ttk.Label(
    frame,
    text='Выберите пару и нажмите кнопку',
    justify=LEFT,
    wraplength=360,
    font=('TkDefaultFont', 11, 'bold'),
)
result_label.pack(anchor=W)

coin_combobox.set('bitcoin')
update_coin_label()
quote_combobox.set('usd')
update_quote_label()

root.mainloop()
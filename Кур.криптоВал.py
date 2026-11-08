# --- Импорты ---------------------------------------------------------------
import json
import urllib.error
import urllib.request

import tkinter as tk
from tkinter import ttk
from tkinter.constants import BOTH, W, X, LEFT

# --- Данные ----------------------------------------------------------------

# id монеты на CoinGecko -> читаемое название
cryptocurrencies = {
    'bitcoin': 'Биткоин (BTC)',
    'ethereum': 'Эфириум (ETH)',
    'litecoin': 'Лайткоин (LTC)',
    'solana': 'Солана (SOL)',
    'cardano': 'Кардано (ADA)',
    'dogecoin': 'Догикоин (DOGE)',
}

# id валюты котировки -> читаемое название
quote_currencies = {
    'usd': 'Доллар США (USD)',
    'eur': 'Евро (EUR)',
    'rub': 'Российский рубль (RUB)',
    'gbp': 'Фунт стерлингов (GBP)',
}

API_URL = 'https://api.coingecko.com/api/v3/simple/price'

def fetch_rate(coin_id: str, quote_id: str) -> float:
    """Возвращает курс coin_id в quote_id. Бросает исключение при ошибке."""
    url = f'{API_URL}?ids={coin_id}&vs_currencies={quote_id}'
    request = urllib.request.Request(
        url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        data = json.loads(response.read().decode('utf-8'))

    if coin_id not in data or quote_id not in data[coin_id]:
        raise ValueError('В ответе API нет нужной пары')
    return float(data[coin_id][quote_id])

def main() -> None:
    root = tk.Tk()
    root.title('Курсы криптовалют')
    root.geometry('400x320')
    root.resizable(False, False)

    # --- Обработчики (объявлены внутри main, чтобы видеть виджеты) ----------
    def update_coin_label(event=None):
        coin_id = coin_combobox.get()
        coin_label.config(text=cryptocurrencies.get(coin_id, ''))

    def update_quote_label(event=None):
        quote_id = quote_combobox.get()
        quote_label.config(text=quote_currencies.get(quote_id, ''))

    def get_crypto_rate():
        coin_id = coin_combobox.get()
        quote_id = quote_combobox.get()

        if not coin_id or not quote_id:
            result_label.config(text='Выберите криптовалюту и валюту котировки')
            return

        result_label.config(text='Загружаю курс…')
        button.config(state='disabled')
        root.update_idletasks()  # чтобы надпись появилась сразу

        try:
            rate = fetch_rate(coin_id, quote_id)
        except urllib.error.HTTPError as exc:
            result_label.config(
                text=f'Ошибка сервера: HTTP {exc.code}. '
                     'Возможно, исчерпан лимит запросов.'
            )
        except urllib.error.URLError:
            result_label.config(text='Нет соединения. Проверьте интернет.')
        except (TimeoutError, OSError):
            result_label.config(text='Превышено время ожидания ответа.')
        except (ValueError, KeyError):
            result_label.config(text='Не удалось разобрать ответ API.')
        else:
            name = cryptocurrencies.get(coin_id, coin_id)
            quote = quote_currencies.get(quote_id, quote_id)
            result_label.config(
                text=f'1 {coin_id.capitalize()} = {rate:,.2f} {quote_id.upper()}\n'
                     f'({name} в {quote})'
            )
        finally:
            button.config(state='normal')

    # --- Внешний контейнер ---------------------------------------------------
    frame = ttk.Frame(root, padding=12)
    frame.pack(fill=BOTH, expand=True)

    # --- Первый блок: выбор криптовалюты -------------------------------------
    ttk.Label(frame, text='Криптовалюта').pack(anchor=W)

    coin_combobox = ttk.Combobox(
        frame,
        values=list(cryptocurrencies.keys()),
        state='readonly',
    )
    coin_combobox.pack(fill=X, pady=(3, 0))
    coin_combobox.bind('<<ComboboxSelected>>', update_coin_label)

    coin_label = ttk.Label(frame, foreground='#555555')
    coin_label.pack(anchor=W, pady=(2, 8))

    # --- Второй блок: выбор валюты котировки ---------------------------------
    ttk.Label(frame, text='Валюта котировки').pack(anchor=W)

    quote_combobox = ttk.Combobox(
        frame,
        values=list(quote_currencies.keys()),
        state='readonly',
    )
    quote_combobox.pack(fill=X, pady=(3, 0))
    quote_combobox.bind('<<ComboboxSelected>>', update_quote_label)

    quote_label = ttk.Label(frame, foreground='#555555')
    quote_label.pack(anchor=W, pady=(2, 8))

    # --- Кнопка запуска запроса ----------------------------------------------
    button = ttk.Button(frame, text='Узнать курс', command=get_crypto_rate)
    button.pack(fill=X, pady=(4, 10))

    # --- Область результата --------------------------------------------------
    result_label = ttk.Label(
        frame,
        text='Выберите пару и нажмите кнопку',
        justify=LEFT,
        wraplength=360,
        font=('TkDefaultFont', 11, 'bold'),
    )
    result_label.pack(anchor=W)

    # --- Начальные значения --------------------------------------------------
    coin_combobox.set('bitcoin')
    update_coin_label()
    quote_combobox.set('usd')
    update_quote_label()

    root.mainloop()

if __name__ == '__main__':
    main()
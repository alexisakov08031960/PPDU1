import datetime
import requests
from tkinter import Tk, Button, ttk, messagebox as mb

COINS = {
    'bitcoin': 'Bitcoin',
    'ethereum': 'Ethereum',
    'binancecoin': 'BNB',
    'cardano': 'Cardano',
    'dogecoin': 'Dogecoin',
}

API_URL = 'https://api.coingecko.com/api/v3/simple/price'
REQUEST_TIMEOUT = 10
REFRESH_INTERVAL = 30  # нельзя чаще чем раз в 30 секунд


def get_rates():
    params = {
        'ids': ','.join(COINS),
        'vs_currencies': 'usd',
        'include_24hr_change': 'true',
    }
    response = requests.get(API_URL, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def update_table(table, data):
    for row in table.get_children():
        table.delete(row)

    for coin_id, name in COINS.items():
        price = data[coin_id]['usd']
        change = data[coin_id].get('usd_24hr_change', 0)

        if change >= 0:
            tag, sign = 'up', '+'
        else:
            tag, sign = 'down', ''

        table.insert(
            '', 'end',
            values=(
                name,
                f'{price:,.2f}'.replace(',', ' '),
                f'{sign}{change:.2f}%',
            ),
            tags=(tag,),
        )


def on_refresh(table, timestamp_label, state):
    now = datetime.datetime.now()

    # Проверка: не слишком ли часто жмут кнопку
    if state['last_refresh'] is not None:
        elapsed = (now - state['last_refresh']).total_seconds()
        if elapsed < REFRESH_INTERVAL:
            left = int(REFRESH_INTERVAL - elapsed)
            mb.showinfo('Слишком часто', f'Данные обновятся через {left} сек.')
            return

    try:
        data = get_rates()
        update_table(table, data)
        state['last_refresh'] = now
        timestamp_label.config(text=f'Обновлено: {now:%d.%m.%Y %H:%M:%S}')
    except requests.RequestException:
        mb.showerror('Ошибка', 'Не удалось получить данные. Проверьте подключение.')
    except (KeyError, ValueError):
        mb.showerror('Ошибка', 'Некорректный ответ сервера.')


def build_gui():
    root = Tk()
    root.title('Курсы криптовалют')
    root.geometry('420x300')
    root.resizable(False, False)

    ttk.Label(root, text='Курс по данным CoinGecko',
              font=('', 11, 'bold')).pack(pady=(10, 5))

    columns = ('coin', 'price', 'change')
    table = ttk.Treeview(root, columns=columns, show='headings', height=6)
    table.heading('coin', text='Монета')
    table.heading('price', text='Цена, $')
    table.heading('change', text='24 ч')
    table.column('coin', width=180, anchor='w')
    table.column('price', width=120, anchor='e')
    table.column('change', width=80, anchor='center')
    table.pack(padx=10, pady=5)

    # Настройка цветов для строк
    table.tag_configure('up', foreground='green')
    table.tag_configure('down', foreground='red')

    timestamp_label = ttk.Label(root, text='Обновлено: ещё не обновлялось')
    timestamp_label.pack(pady=2)

    return root, table, timestamp_label


def main():
    root, table, timestamp_label = build_gui()
    state = {'last_refresh': None}

    Button(root, text='Обновить',
           command=lambda: on_refresh(table, timestamp_label, state)
           ).pack(pady=10)

    root.mainloop()


if __name__ == '__main__':
    main()
from tkinter import *
from tkinter import messagebox as mb
from tkinter import ttk
import requests
import threading
from datetime import datetime

cryptocurrencies = {
    'bitcoin': ('Биткоин', 'BTC'),
    'ethereum': ('Эфириум', 'ETH'),
    'tether': ('Tether', 'USDT'),
    'binancecoin': ('BNB', 'BNB'),
    'solana': ('Solana', 'SOL'),
    'ripple': ('XRP', 'XRP'),
    'cardano': ('Cardano', 'ADA'),
    'dogecoin': ('Dogecoin', 'DOGE'),
    'toncoin': ('Toncoin', 'TON'),
    'tron': ('TRON', 'TRX'),
}

quote_currencies = {
    'usd': ('Доллар США', 'USD'),
    'eur': ('Евро', 'EUR'),
    'rub': ('Российский рубль', 'RUB'),
}

API_URL = 'https://api.coingecko.com/api/v3/simple/price'

BG         = '#0f1117'
CARD       = '#1a1d27'
CARD_ALT   = '#151822'
BORDER     = '#2b2f3d'
ACCENT     = '#f0b90b'
ACCENT_HOV = '#ffd23f'
TEXT       = '#eaecef'
MUTED      = '#8b91a3'
GREEN      = '#2ebd85'
RED        = '#f6465d'

FONT = 'Segoe UI'

def format_price(value: float) -> str:
    if value >= 1:
        return f'{value:,.2f}'
    return f'{value:.8f}'.rstrip('0').rstrip('.')

def bind_hover(widget, normal, hover):
    widget.bind('<Enter>', lambda e: widget.config(bg=hover))
    widget.bind('<Leave>', lambda e: widget.config(bg=normal))

state = {'loading': False, 'prices': {}, 'changes': {}}

def fetch_all():
    state['loading'] = True
    refresh_btn.config(state=DISABLED, bg=CARD, fg=MUTED, text='Загрузка...')
    status_label.config(text='Запрос к CoinGecko...', fg=MUTED)

    try:
        params = {
            'ids': ','.join(cryptocurrencies.keys()),
            'vs_currencies': ','.join(quote_currencies.keys()),
            'include_24hr_change': 'true',
        }
        response = requests.get(API_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        state['prices'] = {}
        state['changes'] = {}
        for coin_id in cryptocurrencies:
            if coin_id not in data:
                continue
            state['prices'][coin_id] = {
                q: data[coin_id].get(q) for q in quote_currencies
            }
            state['changes'][coin_id] = {
                q: data[coin_id].get(f'{q}_24h_change') for q in quote_currencies
            }

        render_table()
        status_label.config(
            text=f'Обновлено: {datetime.now():%H:%M:%S} · монет: {len(state["prices"])}',
            fg=GREEN,
        )
    except requests.exceptions.Timeout:
        mb.showerror('Ошибка', 'Превышено время ожидания ответа от сервера')
        status_label.config(text='Ошибка: таймаут', fg=RED)
    except requests.exceptions.RequestException as er:
        mb.showerror('Ошибка сети', str(er))
        status_label.config(text='Ошибка сети', fg=RED)
    except Exception as er:
        mb.showerror('Ошибка', er)
        status_label.config(text='Ошибка', fg=RED)
    finally:
        state['loading'] = False
        refresh_btn.config(state=NORMAL, bg=ACCENT, fg=BG, text='Обновить курсы')

def refresh_async():
    if state['loading']:
        return
    threading.Thread(target=fetch_all, daemon=True).start()

def render_table():
    for row in table.get_children():
        table.delete(row)

    sort_key = sort_var.get()
    ids = list(cryptocurrencies.keys())

    if sort_key != 'name':
        def keyfunc(cid):
            v = state['prices'].get(cid, {}).get(sort_key.replace('delta_', ''))
            return v if v is not None else float('-inf')
        ids.sort(key=keyfunc, reverse=not rising_var.get())

    for i, cid in enumerate(ids):
        name, ticker = cryptocurrencies[cid]
        prices = state['prices'].get(cid, {})
        changes = state['changes'].get(cid, {})

        change_usd = changes.get('usd')
        if change_usd is None:
            chg_text, chg_color = '—', MUTED
        else:
            arrow = '▲' if change_usd >= 0 else '▼'
            chg_text = f'{arrow} {change_usd:+.2f} %'
            chg_color = GREEN if change_usd >= 0 else RED

        values = (
            ticker,
            name,
            f'{format_price(prices["usd"]):>14}' if prices.get('usd') is not None else '—',
            f'{format_price(prices["eur"]):>12}' if prices.get('eur') is not None else '—',
            f'{format_price(prices["rub"]):>16}' if prices.get('rub') is not None else '—',
            chg_text,
        )

        tag_moves = 'up' if (change_usd is not None and change_usd >= 0) else (
            'down' if change_usd is not None else ''
        )
        tags = tuple(t for t in (tag_moves, 'odd' if i % 2 else 'even') if t)
        table.insert('', END, values=values, tags=tags)

def toggle_sort():
    rising_var.set(not rising_var.get())
    direction_btn.config(text='▲ По возрастанию' if rising_var.get() else '▼ По убыванию')
    render_table()

root = Tk()
root.title('Курсы криптовалют')
root.geometry('900x780')
root.resizable(False, False)
root.config(bg=BG)

header = Frame(root, bg=BG)
header.pack(fill=X, padx=18, pady=(16, 4))

Label(header, text='₿ Курсы криптовалют — сводная таблица',
      bg=BG, fg=TEXT, font=(FONT, 17, 'bold')).pack(anchor=W)

Label(header, text='Все монеты ко всем валютам · один запрос к CoinGecko',
      bg=BG, fg=MUTED, font=(FONT, 9)).pack(anchor=W, pady=(2, 0))

controls = Frame(root, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
controls.pack(fill=X, padx=18, pady=(10, 8))
cin = Frame(controls, bg=CARD)
cin.pack(fill=X, padx=14, pady=12)

refresh_btn = Button(
    cin, text='Обновить курсы', command=refresh_async,
    bg=ACCENT, fg=BG, activebackground=ACCENT_HOV, activeforeground=BG,
    font=(FONT, 10, 'bold'), relief=FLAT, bd=0, cursor='hand2',
    padx=16, pady=7,
)
refresh_btn.pack(side=LEFT)
bind_hover(refresh_btn, ACCENT, ACCENT_HOV)

Label(cin, text='Сортировать:', bg=CARD, fg=MUTED,
      font=(FONT, 9)).pack(side=LEFT, padx=(18, 6))

sort_var = StringVar(value='usd')
sort_box = ttk.Combobox(
    cin, state='readonly', width=14, font=(FONT, 9),
    values=['name', 'usd', 'eur', 'rub'],
    textvariable=sort_var,
)
sort_box.pack(side=LEFT)
sort_box.bind('<<ComboboxSelected>>', lambda e: render_table())

rising_var = BooleanVar(value=False)
direction_btn = Button(
    cin, text='▼ По убыванию', command=toggle_sort,
    bg=CARD_ALT, fg=TEXT, activebackground=BORDER, activeforeground=TEXT,
    font=(FONT, 9), relief=FLAT, bd=0, cursor='hand2', padx=10, pady=6,
)
direction_btn.pack(side=LEFT, padx=(8, 0))
bind_hover(direction_btn, CARD_ALT, BORDER)

status_label = Label(cin, text='Нажмите «Обновить курсы»', bg=CARD, fg=MUTED,
                     font=(FONT, 9))
status_label.pack(side=RIGHT)

style = ttk.Style(root)
style.theme_use('clam')
style.configure('Crypto.Treeview', background=CARD, fieldbackground=CARD,
                foreground=TEXT, rowheight=28, borderwidth=0, font=(FONT, 9))
style.configure('Crypto.Treeview.Heading', background=CARD_ALT, foreground=MUTED,
                font=(FONT, 8, 'bold'), relief=FLAT, borderwidth=0, padding=6)
style.map('Crypto.Treeview.Heading', background=[('active', BORDER)])
style.map('Crypto.Treeview', background=[('selected', BORDER)],
          foreground=[('selected', ACCENT)])

table_frame = Frame(root, bg=BG)
table_frame.pack(fill=BOTH, expand=True, padx=18, pady=(6, 16))

columns = ('ticker', 'name', 'usd', 'eur', 'rub', 'change')
table = ttk.Treeview(table_frame, columns=columns, show='headings',
                     height=10, style='Crypto.Treeview')

table.heading('ticker', text='ТИКЕР')
table.heading('name', text='МОНЕТА')
table.heading('usd', text='ЦЕНА, USD')
table.heading('eur', text='ЦЕНА, EUR')
table.heading('rub', text='ЦЕНА, RUB')
table.heading('change', text='ЗА 24 Ч')

table.column('ticker', width=80, anchor=CENTER)
table.column('name', width=150, anchor=W)
table.column('usd', width=150, anchor=E)
table.column('eur', width=140, anchor=E)
table.column('rub', width=170, anchor=E)
table.column('change', width=110, anchor=E)

scroll = Scrollbar(table_frame, orient=VERTICAL, command=table.yview,
                   bg=CARD, troughcolor=BG, activebackground=BORDER,
                   relief=FLAT, bd=0, width=10)
table.configure(yscrollcommand=scroll.set)
table.pack(side=LEFT, fill=BOTH, expand=True)
scroll.pack(side=RIGHT, fill=Y)

table.tag_configure('up', foreground=GREEN)
table.tag_configure('down', foreground=RED)
table.tag_configure('odd', background=CARD)
table.tag_configure('even', background=CARD_ALT)

# Двойной клик по строке — подробности пары
def show_details(event=None):
    sel = table.selection()
    if not sel:
        return
    values = table.item(sel[0], 'values')
    mb.showinfo('Информация', '\n'.join(f'{k}: {v}' for k, v in zip(
        ('Тикер', 'Монета', 'USD', 'EUR', 'RUB', '24 ч'), values)))

table.bind('<Double-1>', show_details)

root.mainloop()
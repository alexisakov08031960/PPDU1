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

def update_coin_label(event=None):
    coin_label.config(text=cryptocurrencies.get(coin_combobox.get(), ''))

def update_quote_label(event=None):
    quote_label.config(text=quote_currencies.get(quote_combobox.get(), ''))

def set_result(main: str, sub: str = '', color: str = TEXT):
    result_label.config(text=main, fg=color)
    result_sub.config(text=sub)

def restripe():
    """Чередование фона строк, цветовой тег up/down сохраняется."""
    for i, item in enumerate(table.get_children()):
        tags = [t for t in table.item(item, 'tags') if t not in ('odd', 'even')]
        tags.append('odd' if i % 2 else 'even')
        table.item(item, tags=tags)

def clear_history():
    for row in table.get_children():
        table.delete(row)
    counter_label.config(text='Запросов: 0')

def fetch_price():
    coin_id = coin_combobox.get().strip()
    quote = quote_combobox.get().strip()

    if not coin_id or not quote:
        mb.showwarning('Внимание', 'Выберите криптовалюту и валюту котировки')
        return

    button.config(state=DISABLED, bg=CARD, fg=MUTED, text='Загрузка...')
    set_result('Запрос к API...', '', MUTED)

    try:
        params = {
            'ids': coin_id,
            'vs_currencies': quote,
            'include_24hr_change': 'trтерфейсue',
        }
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if coin_id not in data or quote not in data[coin_id]:
            mb.showerror('Ошибка', f'Данные для {coin_id} не найдены')
            set_result('Выберите пару и нажмите кнопку', '', MUTED)
            return

        price = data[coin_id][quote]
        change = data[coin_id].get(f'{quote}_24h_change')

        coin_name = cryptocurrencies[coin_id]
        quote_name = quote_currencies.get(quote, quote.upper())

        if change is not None:
            arrow = '▲' if change >= 0 else '▼'
            color = GREEN if change >= 0 else RED
            sub = f'{arrow} {change:+.2f} % за 24 ч'
        else:
            color = TEXT
            sub = 'Изменение недоступно'

        set_result(f'{format_price(price)} {quote.upper()}', sub, color)
        coin_caption.config(text=f'1 {coin_name} · {quote_name}')

        tag = '' if change is None else ('up' if change >= 0 else 'down')
        table.insert(
            '', 0,
            values=(
                coin_name,
                quote.upper(),
                format_price(price),
                f'{change:+.2f} %' if change is not None else '—',
            ),
            tags=(tag,),
        )
        restripe()
        counter_label.config(text=f'Запросов: {len(table.get_children())}')

    except requests.exceptions.Timeout:
        mb.showerror('Ошибка', 'Превышено время ожидания ответа от сервера')
        set_result('Выберите пару и нажмите кнопку', '', MUTED)
    except requests.exceptions.RequestException as er:
        mb.showerror('Ошибка сети', str(er))
        set_result('Выберите пару и нажмите кнопку', '', MUTED)
    except Exception as er:
        mb.showerror('Ошибка', er)
        set_result('Выберите пару и нажмите кнопку', '', MUTED)
    finally:
        button.config(state=NORMAL, bg=ACCENT, fg=BG, text='Узнать курс')

def get_crypto_rate():
    threading.Thread(target=fetch_price, daemon=True).start()


root = Tk()
root.title('Курсы криптовалют')
root.geometry('560x680')
root.resizable(False, False)
root.config(bg=BG)

header = Frame(root, bg=BG)
header.pack(fill=X, padx=18, pady=(16, 4))

Label(header, text='₿ Курсы криптовалют', bg=BG, fg=TEXT,
      font=(FONT, 17, 'bold')).pack(anchor=W)

Label(header, text='Данные CoinGecko · обновление в реальном времени',
      bg=BG, fg=MUTED, font=(FONT, 9)).pack(anchor=W, pady=(2, 0))

card = Frame(root, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
card.pack(fill=X, padx=18, pady=(10, 8))
inner = Frame(card, bg=CARD)
inner.pack(fill=X, padx=14, pady=14)

Label(inner, text='КРИПТОВАЛЮТА', bg=CARD, fg=MUTED,
      font=(FONT, 8, 'bold')).pack(anchor=W)

coin_combobox = ttk.Combobox(
    inner, values=list(cryptocurrencies.keys()), state='readonly',
    font=(FONT, 10),
)
coin_combobox.pack(fill=X, pady=(4, 0), ipady=4)
coin_combobox.bind('<<ComboboxSelected>>', update_coin_label)

coin_label = Label(inner, bg=CARD, fg=MUTED, font=(FONT, 9))
coin_label.pack(anchor=W, pady=(3, 12))

Label(inner, text='ВАЛЮТА КОТИРОВКИ', bg=CARD, fg=MUTED,
      font=(FONT, 8, 'bold')).pack(anchor=W)

quote_combobox = ttk.Combobox(
    inner, values=list(quote_currencies.keys()), state='readonly',
    font=(FONT, 10),
)
quote_combobox.pack(fill=X, pady=(4, 0), ipady=4)
quote_combobox.bind('<<ComboboxSelected>>', update_quote_label)

quote_label = Label(inner, bg=CARD, fg=MUTED, font=(FONT, 9))
quote_label.pack(anchor=W, pady=(3, 12))

button = Button(
    inner, text='Узнать курс', command=get_crypto_rate,
    bg=ACCENT, fg=BG,
    activebackground=ACCENT_HOV, activeforeground=BG,
    font=(FONT, 11, 'bold'),
    relief=FLAT, bd=0, cursor='hand2', pady=9,
)
button.pack(fill=X)
bind_hover(button, ACCENT, ACCENT_HOV)

result_card = Frame(root, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
result_card.pack(fill=X, padx=18, pady=(0, 8))
rin = Frame(result_card, bg=CARD)
rin.pack(fill=X, padx=14, pady=14)

coin_caption = Label(rin, text='Выберите пару и нажмите кнопку',
                     bg=CARD, fg=MUTED, font=(FONT, 9))
coin_caption.pack(anchor=W)

result_label = Label(rin, text='—', bg=CARD, fg=MUTED,
                     font=(FONT, 22, 'bold'))
result_label.pack(anchor=W, pady=(2, 0))

result_sub = Label(rin, text='', bg=CARD, fg=MUTED, font=(FONT, 9))
result_sub.pack(anchor=W)

# ---------- История ----------
hist_head = Frame(root, bg=BG)
hist_head.pack(fill=X, padx=18)

Label(hist_head, text='История запросов', bg=BG, fg=TEXT,
      font=(FONT, 11, 'bold')).pack(side=LEFT)

counter_label = Label(hist_head, text='Запросов: 0', bg=BG, fg=MUTED,
                      font=(FONT, 9))
counter_label.pack(side=LEFT, padx=(10, 0))

clear_btn = Button(
    hist_head, text='Очистить', command=clear_history,
    bg=CARD, fg=MUTED,
    activebackground=BORDER, activeforeground=TEXT,
    font=(FONT, 8), relief=FLAT, bd=0, cursor='hand2', padx=8, pady=2,
)
clear_btn.pack(side=RIGHT)
bind_hover(clear_btn, CARD, BORDER)

table_frame = Frame(root, bg=BG)
table_frame.pack(fill=BOTH, expand=True, padx=18, pady=(6, 16))

style = ttk.Style(root)
style.theme_use('clam')
style.configure(
    'Crypto.Treeview',
    background=CARD, fieldbackground=CARD, foreground=TEXT,
    rowheight=26, borderwidth=0, font=(FONT, 9),
)
style.configure(
    'Crypto.Treeview.Heading',
    background=CARD_ALT, foreground=MUTED,
    font=(FONT, 8, 'bold'), relief=FLAT, borderwidth=0,
)
style.map('Crypto.Treeview.Heading', background=[('active', BORDER)])
style.map(
    'Crypto.Treeview',
    background=[('selected', BORDER)],
    foreground=[('selected', ACCENT)],
)

columns = ('coin', 'quote', 'price', 'change')
table = ttk.Treeview(
    table_frame, columns=columns, show='headings', height=8,
    style='Crypto.Treeview',
)

table.heading('coin', text='КРИПТОВАЛЮТА')
table.heading('quote', text='ВАЛЮТА')
table.heading('price', text='ЦЕНА')
table.heading('change', text='ЗА 24 Ч')

table.column('coin', width=210, anchor=W)
table.column('quote', width=70, anchor=CENTER)
table.column('price', width=140, anchor=E)
table.column('change', width=90, anchor=E)

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

coin_combobox.set('bitcoin')
update_coin_label()
quote_combobox.set('usd')
update_quote_label()

root.mainloop()
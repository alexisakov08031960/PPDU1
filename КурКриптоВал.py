# --- Построение интерфейса --------------------------------------------------
root = Tk()
root.title('Курсы криптовалют')
root.geometry('400x320')          # фиксированный размер окна
root.resizable(False, False)      # запрещаем растягивать — вёрстка подогнана под этот размер

# Внешний контейнер с отступами 12 px по всем сторонам.
# fill=BOTH + expand=True — рамка занимает всё окно и тянется вместе с ним.
frame = ttk.Frame(root, padding=12)
frame.pack(fill=BOTH, expand=True)

# --- Первый блок: выбор криптовалюты ---
ttk.Label(frame, text='Криптовалюта').pack(anchor=W)  # заголовок блока, прижат влево

coin_combobox = ttk.Combobox(
    frame,
    values=list(cryptocurrencies.keys()),  # только ключи: пользователь видит id монеты
    state='readonly',                      # запрет на ручной ввод — только выбор из списка
)
coin_combobox.pack(fill=X, pady=(3, 0))    # растягивается по ширине; отступ сверху 3 px
# Событие срабатывает при выборе пункта — обновляем подпись с расшифровкой.
coin_combobox.bind('<<ComboboxSelected>>', update_coin_label)

# Серая подпись-расшифровка под списком (например, 'Биткоин (BTC)').
coin_label = ttk.Label(frame, foreground='#555555')
coin_label.pack(anchor=W, pady=(2, 8))

# --- Второй блок: выбор валюты котировки ---
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

# --- Кнопка запуска запроса ---
button = ttk.Button(frame, text='Узнать курс', command=get_crypto_rate)
button.pack(fill=X, pady=(4, 10))   # во всю ширину, с отступами сверху и снизу

# --- Область результата ---
result_label = ttk.Label(
    frame,
    text='Выберите пару и нажмите кнопку',
    justify=LEFT,               # многострочный текст выравнивается по левому краю
    wraplength=360,             # перенос длинных строк (ширина окна минус отступы)
    font=('TkDefaultFont', 11, 'bold'),  # чуть крупнее и жирнее — это главный вывод
)
result_label.pack(anchor=W)

# --- Начальные значения ---
# По умолчанию выбраны Bitcoin и USD; подписи нужно обновить вручную,
# потому что программная установка значения НЕ вызывает событие <<ComboboxSelected>>.
coin_combobox.set('bitcoin')
update_coin_label()
quote_combobox.set('usd')
update_quote_label()

# Запуск главного цикла обработки событий — окно открывается и ждёт действий.
root.mainloop()

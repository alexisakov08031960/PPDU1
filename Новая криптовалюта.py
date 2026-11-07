"""
Приложение «Курсы криптовалют» на Tkinter.

Что делает программа:
  1. Показывает два выпадающих списка: криптовалюта и валюта котировки.
  2. По нажатию кнопки запрашивает цену у публичного API CoinGecko.
  3. Показывает цену и изменение за 24 часа.

Ключевая идея: запрос к сети выполняется в отдельном потоке,
поэтому окно не «зависает», пока сервер отвечает.
"""

# --- Импорт библиотек -------------------------------------------------------
# Классический стиль Tkinter — «звёздочный» импорт: подтягивает все виджеты
# (Tk, Label, ttk, константы W, X, LEFT, DISABLED и т. д.) в текущее пространство имён.
from tkinter import *
# Диалоговые окна: showwarning / showerror.
from tkinter import messagebox as mb
# Тематические (более современно выглядящие) виджеты: ttk.Frame, ttk.Combobox и др.
from tkinter import ttk

# HTTP-клиент для обращения к REST API.
import requests
# Модуль потоков — чтобы сетевой запрос не блокировал главный цикл интерфейса.
import threading

# --- Справочники ------------------------------------------------------------
# Словарь: идентификатор монеты в API CoinGecko -> человекочитаемое название.
# Ключи (bitcoin, ethereum, ...) — это именно те id, которые понимает API.
# Значения выводятся пользователю, поэтому содержат и название, и тикер.
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

# Словарь валют котировки: код в API -> подпись для пользователя.
# Это «валюта, в которой выражена цена» (сколько рублей/долларов стоит монета).
quote_currencies = {
    'usd': 'Доллар США (USD)',
    'eur': 'Евро (EUR)',
    'rub': 'Российский рубль (RUB)',
}

# Эндпоинт CoinGecko для «простой» цены: отдаёт цену без лишних метаданных.
API_URL = 'https://api.coingecko.com/api/v3/simple/price'

# --- Вспомогательные функции ------------------------------------------------
def format_price(value: float) -> str:
    """
    Форматирует число для вывода.

    Проблема: у криптовалют разброс цен огромный — биткоин стоит десятки тысяч,
    а некоторые монеты — доли цента. Поэтому:
      * если цена >= 1 — выводим 2 знака после запятой и разделитель тысяч;
      * если цена < 1 — выводим до 8 знаков, но обрезаем «хвостовые» нули.

    Примеры:
        format_price(65432.1)   -> '65,432.10'
        format_price(0.00001234)-> '0.00001234'
        format_price(0.5)       -> '0.5'
    """
    if value >= 1:
        # Запятая как разделитель тысяч (стиль en_US), две цифры после точки.
        return f'{value:,.2f}'
    # 8 знаков после точки, затем убираем нули справа и возможную «висячую» точку.
    return f'{value:.8f}'.rstrip('0').rstrip('.')

def update_coin_label(event=None):
    """
    Обновляет серую подпись под списком криптовалют.

    Вызывается двух способами:
      * из кода (после начальной установки значения) — без аргументов;
      * как обработчик события '<<ComboboxSelected>>' — тогда Tkinter
        передаёт объект события, поэтому параметр event нужен,
        хотя внутри функции он не используется.
    """
    code = coin_combobox.get()          # текущий id монеты из словаря
    coin_label.config(text=cryptocurrencies.get(code, ''))  # get с '' — защита от неизвестного кода

def update_quote_label(event=None):
    """То же самое для второй подписи — под списком валют котировки."""
    code = quote_combobox.get()
    quote_label.config(text=quote_currencies.get(code, ''))

def fetch_price():
    """
    Основная рабочая функция: запрашивает данные у CoinGecko и выводит результат.

    ВНИМАНИЕ: выполняется в фоновом потоке (см. get_crypto_rate),
    поэтому внутри нельзя напрямую создавать новые виджеты — только
    менять уже существующие через .config(), что Tkinter допускает.
    """
    # strip() на всякий случай: у Combobox значение может содержать пробелы.
    coin_id = coin_combobox.get().strip()
    quote = quote_combobox.get().strip()

    # Простейшая валидация: пустое значение = нажали, ничего не выбрав.
    if not coin_id or not quote:
        mb.showwarning('Внимание', 'Выберите криптовалюту и валюту котировки')
        return

    # Блокируем кнопку и показываем статус — чтобы не отправить запрос дважды
    # и чтобы пользователь понимал, что идёт работа.
    button.config(state=DISABLED, text='Загрузка...')
    result_label.config(text='Запрос к API...')
    # Принудительно перерисовываем интерфейс прямо сейчас,
    # не дожидаясь возврата в главный цикл (иначе статус появится слишком поздно).
    root.update_idletasks()

    try:
        # Параметры запроса:
        #   ids             — какие монеты (можно несколько через запятую);
        #   vs_currencies   — в каких валютах вернуть цену;
        #   include_24hr_change — попросить также изменение цены за сутки (в процентах).
        params = {
            'ids': coin_id,
            'vs_currencies': quote,
            'include_24hr_change': 'true',
        }

        # timeout=10 обязателен: без него при «зависшем» сервере поток будет ждать вечно.
        response = requests.get(API_URL, params=params, timeout=10)
        # Превращаем HTTP-ошибки (4xx/5xx) в исключение, чтобы поймать их ниже.
        response.raise_for_status()
        # JSON ответа имеет вид: {'bitcoin': {'usd': 65000, 'usd_24h_change': 1.23}, ...}
        data = response.json()

        # Защита от «формально успешного», но пустого ответа:
        # например, сервер не знает такой id монеты.
        if coin_id not in data or quote not in data[coin_id]:
            mb.showerror('Ошибка', f'Данные для {coin_id} не найдены')
            result_label.config(text='')
            return

        price = data[coin_id][quote]
        # .get(), а не [] — ключа изменения может не быть, это не критично.
        change = data[coin_id].get(f'{quote}_24h_change')

        coin_name = cryptocurrencies[coin_id]
        # Если валюта есть в словаре — берём подпись, иначе просто код в верхнем регистре.
        quote_name = quote_currencies.get(quote, quote.upper())

        text = f'1 {coin_name} = {format_price(price)} {quote.upper()}'
        if change is not None:
            # Стрелка вверх/вниз по знаку изменения; {change:+.2f} — знак «+» для роста.
            arrow = '▲' if change >= 0 else '▼'
            text += f'\nИзменение за 24 ч: {arrow} {change:+.2f} %'

        result_label.config(text=text)

    except requests.exceptions.Timeout:
        # Сервер не ответил за 10 секунд.
        mb.showerror('Ошибка', 'Превышено время ожидания ответа от сервера')
        result_label.config(text='')
    except requests.exceptions.RequestException as er:
        # Все прочие сетевые проблемы: нет интернета, DNS, 4xx/5xx, обрыв соединения.
        mb.showerror('Ошибка сети', str(er))
        result_label.config(text='')
    except Exception as er:
        # Страховка от непредвиденного (например, изменился формат JSON).
        mb.showerror('Ошибка', er)
        result_label.config(text='')
    finally:
        # finally выполнится при любом исходе — кнопка гарантированно разблокируется.
        button.config(state=NORMAL, text='Узнать курс')

def get_crypto_rate():
    """
    Обработчик нажатия кнопки.

    Сам запрос запускается в отдельном демоническом потоке:
      * daemon=True — поток не помешает программе закрыться;
      * интерфейс остаётся отзывчивым, пока идёт сетевой запрос.
    """
    threading.Thread(target=fetch_price, daemon=True).start()
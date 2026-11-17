import requests
import tkinter as tk
from tkinter import messagebox, ttk


class CryptoApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Мониторинг криптовалют")
        self.root.geometry("400x320")
        self.root.resizable(False, False)

        # Настройка стилей
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Список криптовалют
        self.crypto_dict = {
            "Bitcoin (BTC)": "bitcoin",
            "Ethereum (ETH)": "ethereum",
            "Binance Coin (BNB)": "binancecoin",
            "Solana (SOL)": "solana",
            "Ripple (XRP)": "ripple",
        }

        self.create_widgets()

    def create_widgets(self):

        # Заголовок
        header = ttk.Label(
            self.root,
            text="Курсы криптовалют",
            font=("Arial", 16, "bold")
        )
        header.pack(pady=15)

        # Выбор валюты
        select_frame = ttk.Frame(self.root)
        select_frame.pack(pady=10)

        label_select = ttk.Label(
            select_frame,
            text="Выберите валюту:",
            font=("Arial", 11)
        )
        label_select.pack(side=tk.LEFT, padx=5)

        self.crypto_chooser = ttk.Combobox(
            select_frame,
            values=list(self.crypto_dict.keys()),
            state="readonly",
            width=18
        )

        self.crypto_chooser.current(0)
        self.crypto_chooser.pack(side=tk.LEFT, padx=5)

        # Отображение цены
        self.price_label = ttk.Label(
            self.root,
            text="$ 0.00",
            font=("Arial", 22, "bold"),
            foreground="#2e7d32"
        )
        self.price_label.pack(pady=20)

        # Кнопка обновления
        self.refresh_btn = ttk.Button(
            self.root,
            text="Получить курс",
            command=self.get_crypto_price
        )
        self.refresh_btn.pack(pady=10)

        # Статус приложения
        self.status_label = ttk.Label(
            self.root,
            text="Приложение готово к работе",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(
            side=tk.BOTTOM,
            fill=tk.X
        )

    def get_crypto_price(self):

        selected_name = self.crypto_chooser.get()
        crypto_id = self.crypto_dict.get(selected_name)

        if not crypto_id:
            messagebox.showerror(
                "Ошибка",
                "Выберите криптовалюту из списка."
            )
            return

        self.status_label.config(text="Загрузка данных...")
        self.root.update_idletasks()

        # Адрес API CoinGecko
        url = "https://api.coingecko.com/api/v3/simple/price"

        params = {
            "ids": crypto_id,
            "vs_currencies": "usd"
        }

        try:
            response = requests.get(
                url,
                params=params,
                timeout=10
            )

            response.raise_for_status()

            data = response.json()

            price = data.get(crypto_id, {}).get("usd")

            if price is not None:

                self.price_label.config(
                    text=f"${price:,.2f}"
                )

                self.status_label.config(
                    text="Курс успешно обновлен"
                )

            else:
                messagebox.showwarning(
                    "Предупреждение",
                    "Не удалось найти цену в ответе API."
                )

                self.status_label.config(
                    text="Ошибка получения данных"
                )

        except requests.exceptions.RequestException as e:

            messagebox.showerror(
                "Ошибка сети",
                f"Не удалось подключиться к серверу:\n{e}"
            )

            self.status_label.config(
                text="Ошибка соединения"
            )
        except (ValueError, TypeError) as e:

            messagebox.showerror(
                "Ошибка данныхх",
                f"Не удалось обработать ответ API:\n{e}"
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoApp(root)
    root.mainloop()
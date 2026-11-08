"""Crypto Rates — графический интерфейс на Tkinter."""

import threading
from datetime import datetime
from tkinter import END, StringVar, Tk, messagebox
from tkinter import ttk

from api import ApiError, fetch_rates

REFRESH_COOLDOWN = 30

def fmt_price(value):
    if value is None:
        return "—"
    if value < 1:
        return f"{value:.6f}"
    return f"{value:,.2f}".replace(",", " ")

def fmt_cap(value):
    if value is None:
        return "—"
    for limit, suffix in ((1e12, "T"), (1e9, "B"), (1e6, "M")):
        if value >= limit:
            return f"{value / limit:,.1f} {suffix}".replace(",", " ")
    return f"{value:,.0f}".replace(",", " ")

def fmt_change(value):
    if value is None:
        return "—"
    return f"{value:+.2f}%"

class CryptoApp:
    COLUMNS = (
        ("name", "Монета", 160),
        ("symbol", "Тикер", 70),
        ("price", "Цена (USD)", 140),
        ("change", "24 ч", 90),
        ("cap", "Капитализация", 130),
    )

    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Rates — курсы криптовалют к USD")
        self.root.geometry("720x480")
        self.root.minsize(640, 400)

        self.loading = False
        self.can_refresh_at = 0.0

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        top = ttk.Frame(self.root, padding=(12, 12, 12, 6))
        top.pack(fill="x")

        ttk.Label(
            top,
            text="Курсы криптовалют к доллару США",
            font=("Segoe UI", 14, "bold"),
        ).pack(side="left")

        self.refresh_btn = ttk.Button(
            top, text="Обновить", command=self.refresh
        )
        self.refresh_btn.pack(side="right")

        body = ttk.Frame(self.root, padding=(12, 0, 12, 6))
        body.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            body,
            columns=[c[0] for c in self.COLUMNS],
            show="headings",
            selectmode="browse",
        )
        for key, title, width in self.COLUMNS:
            self.tree.heading(key, text=title)
            self.tree.column(
                key,
                width=width,
                anchor="w" if key in ("name", "symbol") else "e",
            )
        self.tree.tag_configure("up", foreground="#1a7f37")
        self.tree.tag_configure("down", foreground="#c62828")

        scroll = ttk.Scrollbar(
            body, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        bottom = ttk.Frame(self.root, padding=(12, 0, 12, 10))
        bottom.pack(fill="x")

        self.status = StringVar(value="Готово к загрузке")
        ttk.Label(
            bottom, textvariable=self.status, foreground="#555555"
        ).pack(side="left")

    def refresh(self):
        if self.loading:
            return
        self.loading = True
        self.refresh_btn.state(["disabled"])
        self.status.set("Загрузка данных…")
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        try:
            rates = fetch_rates()
        except ApiError as exc:
            self.root.after(0, self._on_error, str(exc))
        else:
            self.root.after(0, self._on_success, rates)

    def _on_success(self, rates):
        self.tree.delete(*self.tree.get_children())
        for row in rates:
            change = row["change_24h"] or 0
            tag = "up" if change >= 0 else "down"
            self.tree.insert(
                "",
                END,
                values=(
                    row["name"],
                    row["symbol"],
                    fmt_price(row["price"]),
                    fmt_change(row["change_24h"]),
                    fmt_cap(row["market_cap"]),
                ),
                tags=(tag,),
            )
        stamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        self.status.set(f"Данные: CoinGecko · Обновлено: {stamp}")
        self._finish()

    def _on_error(self, message):
        self.status.set(f"Ошибка: {message}")
        messagebox.showwarning("Не удалось обновить данные", message)
        self._finish()

    def _finish(self):
        self.loading = False
        self.refresh_btn.state(["!disabled"])

def main():
    root = Tk()
    try:
        ttk.Style().theme_use("clam")
    except Exception:
        pass
    CryptoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Tkinter GUI for the CoinGecko cross-rate app."""

import importlib.util
import queue
import sys
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk

MIN_REFRESH_SECONDS = 15

def load_core_module():
    """Загружает crypto_cross_rates.py из папки рядом с этим файлом."""
    module_path = Path(__file__).resolve().parent / "crypto_cross_rates.py"

    if not module_path.is_file():
        raise FileNotFoundError(
            "Не найден файл crypto_cross_rates.py.\n"
            "Поместите его в ту же папку, что и файл программы GUI:\n"
            f"{module_path.parent}"
        )

    spec = importlib.util.spec_from_file_location("crypto_cross_rates", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Не удалось загрузить модуль:\n{module_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

try:
    core = load_core_module()
except (FileNotFoundError, ImportError) as error:
    raise SystemExit(str(error))

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Crypto cross rates — CoinGecko")
        self.geometry("1020x620")
        self.minsize(860, 520)

        self.coins = []
        self.selected = set()
        self.current = []
        self.refresh_job = None
        self.results = queue.Queue()

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(100, self._poll_results)
        self.load_list()

    def _build_ui(self):
        pad = {"padx": 8, "pady": 6}

        top = ttk.Frame(self)
        top.pack(fill="x", **pad)
        ttk.Label(top, text="Coins to load:").pack(side="left")

        self.top_var = tk.StringVar(value=str(core.DEFAULT_TOP))
        ttk.Spinbox(
            top, from_=3, to=250, width=5, textvariable=self.top_var
        ).pack(side="left", padx=(4, 8))

        self.reload_btn = ttk.Button(top, text="Reload list", command=self.load_list)
        self.reload_btn.pack(side="left")

        self.status_var = tk.StringVar(value="")
        ttk.Label(top, textvariable=self.status_var, foreground="#555").pack(side="right")

        body = ttk.PanedWindow(self, orient="horizontal")
        body.pack(fill="both", expand=True, **pad)

        left = ttk.Frame(body)
        body.add(left, weight=1)

        search_row = ttk.Frame(left)
        search_row.pack(fill="x")
        ttk.Label(search_row, text="Search:").pack(side="left")

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._fill_list())
        ttk.Entry(search_row, textvariable=self.search_var).pack(
            side="left", fill="x", expand=True, padx=(4, 0)
        )

        list_frame = ttk.Frame(left)
        list_frame.pack(fill="both", expand=True, pady=(6, 0))

        columns = ("rank", "symbol", "name", "price")
        self.list_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", selectmode="extended"
        )

        for col, title, width, anchor in (
            ("rank", "#", 40, "e"),
            ("symbol", "Symbol", 70, "w"),
            ("name", "Name", 160, "w"),
            ("price", "Price, USD", 120, "e"),
        ):
            self.list_tree.heading(col, text=title)
            self.list_tree.column(
                col, width=width, anchor=anchor, stretch=(col == "name")
            )

        scroll = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.list_tree.yview
        )
        self.list_tree.configure(yscrollcommand=scroll.set)
        self.list_tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.list_tree.bind("<<TreeviewSelect>>", self._on_select)

        self.sel_var = tk.StringVar(value="Selected: 0/3")
        ttk.Label(left, textvariable=self.sel_var).pack(anchor="w", pady=(6, 0))

        right = ttk.Frame(body)
        body.add(right, weight=1)

        controls = ttk.Frame(right)
        controls.pack(fill="x")

        self.calc_btn = ttk.Button(
            controls, text="Calculate", command=self.calculate, state="disabled"
        )
        self.calc_btn.pack(side="left")

        self.auto_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            controls,
            text="Auto-refresh every",
            variable=self.auto_var,
            command=self._schedule_refresh,
        ).pack(side="left", padx=(12, 4))

        self.interval_var = tk.StringVar(value="60")
        ttk.Spinbox(
            controls,
            from_=MIN_REFRESH_SECONDS,
            to=3600,
            increment=15,
            width=5,
            textvariable=self.interval_var,
        ).pack(side="left")

        ttk.Label(controls, text="s").pack(side="left", padx=(2, 0))

        usd_box = ttk.LabelFrame(right, text="Rates to USD")
        usd_box.pack(fill="x", pady=(10, 0))

        self.usd_tree = ttk.Treeview(
            usd_box, columns=("coin", "usd"), show="headings", height=3
        )
        self.usd_tree.heading("coin", text="Coin")
        self.usd_tree.heading("usd", text="1 coin = USD")
        self.usd_tree.column("coin", width=160, anchor="w")
        self.usd_tree.column("usd", width=180, anchor="e")
        self.usd_tree.pack(fill="x", padx=6, pady=6)

        cross_box = ttk.LabelFrame(
            right, text="Cross rates (1 unit of ROW = X units of COLUMN)"
        )
        cross_box.pack(fill="x", pady=(10, 0))

        self.cross_tree = ttk.Treeview(
            cross_box, columns=("row", "c0", "c1", "c2"), show="headings", height=3
        )
        self.cross_tree.heading("row", text="")
        self.cross_tree.column("row", width=70, anchor="w")

        for index in range(3):
            self.cross_tree.heading(f"c{index}", text="")
            self.cross_tree.column(f"c{index}", width=120, anchor="e")

        self.cross_tree.pack(fill="x", padx=6, pady=6)

        self.updated_var = tk.StringVar(value="")
        ttk.Label(right, textvariable=self.updated_var, foreground="#555").pack(
            anchor="w", pady=(8, 0)
        )

    def _run_bg(self, fn, on_ok, on_err):
        """Выполняет работу в фоновом потоке и передаёт результат в UI-поток."""

        def work():
            try:
                result = fn()
            except Exception as error:
                self.results.put((on_err, error))
            else:
                self.results.put((on_ok, result))

        threading.Thread(target=work, daemon=True).start()

    def _poll_results(self):
        try:
            while True:
                callback, argument = self.results.get_nowait()
                callback(argument)
        except queue.Empty:
            pass

        self.after(100, self._poll_results)

    def load_list(self):
        try:
            limit = min(max(int(self.top_var.get()), 3), 250)
        except ValueError:
            limit = core.DEFAULT_TOP

        self.top_var.set(str(limit))
        self.reload_btn.config(state="disabled")
        self.status_var.set("Loading coin list from CoinGecko…")
        self._run_bg(
            lambda: core.fetch_coin_list(limit),
            self._on_list_loaded,
            self._on_list_error,
        )

    def _on_list_loaded(self, coins):
        self.coins = coins
        self.selected &= {coin["id"] for coin in coins}
        self._fill_list()
        self.reload_btn.config(state="normal")
        self.status_var.set(
            f"{len(coins)} coins loaded at {datetime.now():%H:%M:%S}"
        )

    def _on_list_error(self, error):
        self.reload_btn.config(state="normal")
        self.status_var.set("Could not load the coin list")
        messagebox.showerror("CoinGecko", str(error))

    def _fill_list(self):
        query = self.search_var.get().strip().lower()
        self.list_tree.delete(*self.list_tree.get_children())
        visible = []

        for rank, coin in enumerate(self.coins, 1):
            if (
                query
                and query not in coin["name"].lower()
                and query not in coin["symbol"].lower()
                and query not in coin["id"].lower()
            ):
                continue

            self.list_tree.insert(
                "",
                "end",
                iid=coin["id"],
                values=(rank, coin["symbol"], coin["name"], core.fmt(coin["usd"])),
            )
            visible.append(coin["id"])

        keep = [coin_id for coin_id in visible if coin_id in self.selected]
        if keep:
            self.list_tree.selection_set(keep)

        self._update_selection_label()

    def _on_select(self, _event=None):
        visible = set(self.list_tree.get_children())
        self.selected = (self.selected - visible) | set(self.list_tree.selection())
        self._update_selection_label()

    def _update_selection_label(self):
        count = len(self.selected)
        names = [
            coin["symbol"] for coin in self.coins if coin["id"] in self.selected
        ]

        text = f"Selected: {count}/3"
        if names:
            text += f"  ({', '.join(names)})"
        if count > 3:
            text += " — select exactly three"

        self.sel_var.set(text)
        self.calc_btn.config(state="normal" if count == 3 else "disabled")

    def calculate(self):
        chosen = [coin for coin in self.coins if coin["id"] in self.selected]
        if len(chosen) != 3:
            return

        self.current = chosen
        self._fetch_prices(manual=True)

    def _fetch_prices(self, manual):
        if not self.current:
            return

        ids = [coin["id"] for coin in self.current]
        self.status_var.set("Fetching prices…")
        self._run_bg(
            lambda: core.fetch_usd_prices(ids),
            self._on_prices,
            lambda error: self._on_prices_error(error, manual),
        )

    def _on_prices(self, prices):
        coins = self.current
        symbols = [coin["symbol"] for coin in coins]
        usd = [prices[coin["id"]] for coin in coins]

        self.usd_tree.delete(*self.usd_tree.get_children())
        for symbol, price in zip(symbols, usd):
            self.usd_tree.insert(
                "", "end", values=(f"1 {symbol}", core.fmt(price))
            )

        for index, symbol in enumerate(symbols):
            self.cross_tree.heading(f"c{index}", text=symbol)

        self.cross_tree.delete(*self.cross_tree.get_children())
        for row_index, symbol in enumerate(symbols):
            row = [
                symbol,
                *[
                    "—" if row_index == col_index
                    else core.fmt(usd[row_index] / usd[col_index])
                    for col_index in range(3)
                ],
            ]
            self.cross_tree.insert("", "end", values=row)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_var.set(f"Updated {now} (source: CoinGecko)")
        self.status_var.set("Ready")
        self._schedule_refresh()

    def _on_prices_error(self, error, manual):
        self.status_var.set(f"Error: {error}")
        if manual:
            messagebox.showerror("CoinGecko", str(error))
        self._schedule_refresh()

    def _schedule_refresh(self):
        if self.refresh_job is not None:
            self.after_cancel(self.refresh_job)
            self.refresh_job = None

        if not (self.auto_var.get() and self.current):
            return

        try:
            seconds = max(int(self.interval_var.get()), MIN_REFRESH_SECONDS)
        except ValueError:
            seconds = 60

        self.interval_var.set(str(seconds))
        self.refresh_job = self.after(
            seconds * 1000, self._auto_tick
        )

    def _auto_tick(self):
        self.refresh_job = None
        self._fetch_prices(manual=False)

    def _on_close(self):
        if self.refresh_job is not None:
            self.after_cancel(self.refresh_job)
        self.destroy()

def main():
    try:
        app = App()
    except tk.TclError as error:
        raise SystemExit(
            f"Cannot open a window ({error}). Is a display available?"
        )

    app.mainloop()

if __name__ == "__main__":
    main()
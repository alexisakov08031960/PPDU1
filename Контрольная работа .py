import queue
import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

import crypto_cross_rates as core

MIN_REFRESH_SECONDS = 15  # CoinGecko's free tier is rate limited


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Crypto cross rates — CoinGecko")
        self.geometry("1020x620")
        self.minsize(860, 520)

        self.coins = []          # list of coin dicts, ordered by market cap
        self.selected = set()    # selected coin ids (survives list filtering)
        self.current = []        # coin dicts used for the displayed report
        self.refresh_job = None
        self.results = queue.Queue()  # worker threads -> UI thread

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
        ttk.Spinbox(top, from_=3, to=250, width=5, textvariable=self.top_var).pack(side="left", padx=(4, 8))
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
        ttk.Entry(search_row, textvariable=self.search_var).pack(side="left", fill="x", expand=True, padx=(4, 0))

        list_frame = ttk.Frame(left)
        list_frame.pack(fill="both", expand=True, pady=(6, 0))
        cols = ("rank", "symbol", "name", "price")
        self.list_tree = ttk.Treeview(list_frame, columns=cols, show="headings", selectmode="extended")
        for col, text, width, anchor in (
            ("rank", "#", 40, "e"),
            ("symbol", "Symbol", 70, "w"),
            ("name", "Name", 160, "w"),
            ("price", "Price, USD", 120, "e"),
        ):
            self.list_tree.heading(col, text=text)
            self.list_tree.column(col, width=width, anchor=anchor, stretch=(col == "name"))
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.list_tree.yview)
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
        self.calc_btn = ttk.Button(controls, text="Calculate", command=self.calculate, state="disabled")
        self.calc_btn.pack(side="left")
        self.auto_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(controls, text="Auto-refresh every", variable=self.auto_var,
                        command=self._schedule_refresh).pack(side="left", padx=(12, 4))
        self.interval_var = tk.StringVar(value="60")
        ttk.Spinbox(controls, from_=MIN_REFRESH_SECONDS, to=3600, increment=15, width=5,
                    textvariable=self.interval_var).pack(side="left")
        ttk.Label(controls, text="s").pack(side="left", padx=(2, 0))

        usd_box = ttk.LabelFrame(right, text="Rates to USD")
        usd_box.pack(fill="x", pady=(10, 0))
        self.usd_tree = ttk.Treeview(usd_box, columns=("coin", "usd"), show="headings", height=3)
        self.usd_tree.heading("coin", text="Coin")
        self.usd_tree.heading("usd", text="1 coin = USD")
        self.usd_tree.column("coin", width=160, anchor="w")
        self.usd_tree.column("usd", width=180, anchor="e")
        self.usd_tree.pack(fill="x", padx=6, pady=6)

        cross_box = ttk.LabelFrame(right, text="Cross rates (1 unit of ROW = X units of COLUMN)")
        cross_box.pack(fill="x", pady=(10, 0))
        self.cross_tree = ttk.Treeview(cross_box, columns=("row", "c0", "c1", "c2"), show="headings", height=3)
        self.cross_tree.heading("row", text="")
        self.cross_tree.column("row", width=70, anchor="w")
        for i in range(3):
            self.cross_tree.heading(f"c{i}", text="")
            self.cross_tree.column(f"c{i}", width=120, anchor="e")
        self.cross_tree.pack(fill="x", padx=6, pady=6)

        self.updated_var = tk.StringVar(value="")
        ttk.Label(right, textvariable=self.updated_var, foreground="#555").pack(anchor="w", pady=(8, 0))

    def _run_bg(self, fn, on_ok, on_err):
        """Run fn in a thread; deliver the result to the UI thread via a queue."""
        def work():
            try:
                result = fn()
            except Exception as e:  # noqa: BLE001 - shown to the user
                self.results.put((on_err, e))
            else:
                self.results.put((on_ok, result))

        threading.Thread(target=work, daemon=True).start()

    def _poll_results(self):
        try:
            while True:
                callback, arg = self.results.get_nowait()
                callback(arg)
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
        self._run_bg(lambda: core.fetch_coin_list(limit), self._on_list_loaded, self._on_list_error)

    def _on_list_loaded(self, coins):
        self.coins = coins
        self.selected &= {c["id"] for c in coins}
        self._fill_list()
        self.reload_btn.config(state="normal")
        self.status_var.set(f"{len(coins)} coins loaded at {datetime.now():%H:%M:%S}")

    def _on_list_error(self, err):
        self.reload_btn.config(state="normal")
        self.status_var.set("Could not load the coin list")
        messagebox.showerror("CoinGecko", str(err))

    def _fill_list(self):
        query = self.search_var.get().strip().lower()
        self.list_tree.delete(*self.list_tree.get_children())
        visible = []
        for rank, c in enumerate(self.coins, 1):
            if query and query not in c["name"].lower() and query not in c["symbol"].lower() \
                    and query not in c["id"]:
                continue
            self.list_tree.insert("", "end", iid=c["id"],
                                  values=(rank, c["symbol"], c["name"], core.fmt(c["usd"])))
            visible.append(c["id"])
        keep = [i for i in visible if i in self.selected]
        if keep:
            self.list_tree.selection_set(keep)
        self._update_selection_label()

    def _on_select(self, _event=None):
        # Only touch the ids that are currently visible, so selections made
        # before a search filter was applied are not lost.
        visible = set(self.list_tree.get_children())
        self.selected = (self.selected - visible) | set(self.list_tree.selection())
        self._update_selection_label()

    def _update_selection_label(self):
        n = len(self.selected)
        names = [c["symbol"] for c in self.coins if c["id"] in self.selected]
        text = f"Selected: {n}/3" + (f"  ({', '.join(names)})" if names else "")
        if n > 3:
            text += " — select exactly three"
        self.sel_var.set(text)
        self.calc_btn.config(state="normal" if n == 3 else "disabled")

    def calculate(self):
        """Use the three selected coins as the new report and fetch fresh prices."""
        chosen = [c for c in self.coins if c["id"] in self.selected]
        if len(chosen) != 3:
            return
        self.current = chosen
        self._fetch_prices(manual=True)

    def _fetch_prices(self, manual):
        if not self.current:
            return
        ids = [c["id"] for c in self.current]
        self.status_var.set("Fetching prices…")
        self._run_bg(
            lambda: core.fetch_usd_prices(ids),
            self._on_prices,
            lambda e: self._on_prices_error(e, manual),
        )

    def _on_prices(self, prices):
        coins = self.current
        symbols = [c["symbol"] for c in coins]
        usd = [prices[c["id"]] for c in coins]

        self.usd_tree.delete(*self.usd_tree.get_children())
        for s, p in zip(symbols, usd):
            self.usd_tree.insert("", "end", values=(f"1 {s}", core.fmt(p)))

        for i, s in enumerate(symbols):
            self.cross_tree.heading(f"c{i}", text=s)
        self.cross_tree.delete(*self.cross_tree.get_children())
        for i, s in enumerate(symbols):
            row = [s] + ["—" if i == j else core.fmt(usd[i] / usd[j]) for j in range(3)]
            self.cross_tree.insert("", "end", values=row)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_var.set(f"Updated {now} (source: CoinGecko)")
        self.status_var.set("Ready")
        self._schedule_refresh()

    def _on_prices_error(self, err, manual):
        self.status_var.set(f"Error: {err}")
        if manual:
            messagebox.showerror("CoinGecko", str(err))
        self._schedule_refresh()  # keep trying if auto-refresh is on

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
        self.refresh_job = self.after(seconds * 1000, lambda: self._auto_tick())

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
    except tk.TclError as e:
        raise SystemExit(f"Cannot open a window ({e}). Is a display available?")
    app.mainloop()


if __name__ == "__main__":
    main()

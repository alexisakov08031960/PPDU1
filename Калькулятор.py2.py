import os

HISTORY_FILE = "calculations.txt"

def show_history():
    """Читает calculations.txt и выводит все выполненные вычисления."""
    if not os.path.exists(HISTORY_FILE):
        print("\nИстория пуста: файл calculations.txt ещё не создан.")
        return

    with open(HISTORY_FILE, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    if not lines:
        print("\nИстория пуста: вычислений пока не было.")
        return

    print("\n--- ИСТОРИЯ ВЫЧИСЛЕНИЙ ---")
    for number, line in enumerate(lines, start=1):
        print(f"{number}. {line}")
    print(f"Всего записей: {len(lines)}")
import os
from pathlib import Path

HISTORY_FILE = Path('calculations.txt')

def add(x: float, y: float) -> float:
    return x + y

def subtract(x: float, y: float) -> float:
    return x - y

def multiply(x: float, y: float) -> float:
    return x * y

def divide(x: float, y: float) -> float:
    if y == 0:
        raise ZeroDivisionError("Деление на ноль невозможно!")
    return x / y

OPERATIONS = {
    '+': add,
    '-': subtract,
    '*': multiply,
    '/': divide,
}

def format_number(value: float) -> str:
    """Печатает 1.0 как '1', а 0.1 + 0.2 не превращает в мусор."""
    if value.is_integer() and abs(value) < 1e16:
        return str(int(value))
    return f"{value:g}"

def save_to_history(entry: str) -> None:
    """Записывает одну строку вычисления в файл истории."""
    with HISTORY_FILE.open('a', encoding='utf-8') as f:
        f.write(entry + '\n')

def show_history() -> None:
    """Читает файл истории и выводит его содержимое пользователю."""
    try:
        lines = HISTORY_FILE.read_text(encoding='utf-8').splitlines()
    except FileNotFoundError:
        lines = []

    lines = [line for line in lines if line.strip()]
    if not lines:
        print("\nИстория вычислений пуста.\n")
        return

    print("\n--- История вычислений ---")
    for i, line in enumerate(reversed(lines), 1):
        print(f"{i}. {line}")
    print("--------------------------\n")

def read_number(prompt: str) -> float:
    """Читает число, повторяя запрос при ошибке ввода."""
    while True:
        raw = input(prompt).strip().replace(',', '.')
        try:
            value = float(raw)
        except ValueError:
            print("Ошибка: введите корректное число.")
            continue
        if value != value or value in (float('inf'), float('-inf')):
            print("Ошибка: число должно быть конечным.")
            continue
        return value

def main() -> None:
    print("Простой калькулятор")
    print("Доступные операции: +, -, *, /")
    print("Введите 'history' для просмотра истории или 'exit' для выхода.")

    while True:
        try:
            operation = input("\nВведите операцию (+, -, *, /) или команду: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nВыход из калькулятора.")
            break

        command = operation.lower()

        if command == 'exit':
            print("Выход из калькулятора.")
            break
        if command == 'history':
            show_history()
            continue
        if operation not in OPERATIONS:
            print("Некорректная операция. Попробуйте снова.")
            continue

        num1 = read_number("Введите первое число: ")
        num2 = read_number("Введите второе число: ")

        try:
            result = OPERATIONS[operation](num1, num2)
        except ZeroDivisionError as e:
            print(f"Ошибка: {e}")
            continue

        history_entry = f"{format_number(num1)} {operation} {format_number(num2)} = {format_number(result)}"
        print(f"Результат: {format_number(result)}")

        try:
            save_to_history(history_entry)
        except OSError as e:
            print(f"Не удалось сохранить историю: {e}")

if __name__ == "__main__":
    main()
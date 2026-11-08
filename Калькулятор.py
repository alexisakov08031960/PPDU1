import os

HISTORY_FILE = "calculations.txt"

def calculate(a, operator, b, c=None):
    """Выполняет операцию. Для оператора '×' нужно третье число c."""
    if operator == "+":
        return a + b
    if operator == "-":
        return a - b
    if operator == "*":
        return a * b
    if operator == "/":
        if b == 0:
            raise ZeroDivisionError("деление на ноль невозможно")
        return a / b

    # Новая операция: умножение трёх чисел
    if operator in ("×", "x", "*3"):
        if c is None:
            raise ValueError("для умножения трёх чисел нужно третье число")
        return a * b * c

    raise ValueError(f"неизвестная операция: {operator}")

def needs_third_number(operator):
    """Проверяет, требует ли оператор третьего числа."""
    return operator in ("×", "x", "*3")

def save_calculation(expression, result):
    """Дозаписывает вычисление в файл истории."""
    with open(HISTORY_FILE, "a", encoding="utf-8") as file:
        file.write(f"{expression} = {result}\n")

def show_history():
    """Читает файл calculations.txt и выводит историю вычислений."""
    if not os.path.exists(HISTORY_FILE):
        print("\nИстория пуста: файл calculations.txt ещё не создан.")
        return

    with open(HISTORY_FILE, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    if not lines:
        print("\nИстория пуста: вычислений пока не было.")
        return

    print("\n" + "=" * 46)
    print("ИСТОРИЯ ВЫЧИСЛЕНИЙ")
    print("=" * 46)
    for number, line in enumerate(lines, start=1):
        print(f"{number:>3}. {line}")
    print("=" * 46)
    print(f"Всего записей: {len(lines)}")

def get_number(prompt):
    """Запрашивает число, пока пользователь не введёт корректное значение."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Ошибка: введите число, например 12 или 3.5")

def main():
    print("КАЛЬКУЛЯТОР")
    while True:
        print("\nМеню:")
        print("  1 — выполнить вычисление")
        print("  2 — посмотреть историю")
        print("  3 — очистить историю")
        print("  4 — выход")

        choice = input("Выберите пункт: ").strip()

        if choice == "4" or choice.lower() in ("q", "exit", "выход"):
            print("До встречи!")
            break

        if choice == "2":
            show_history()
            continue

        if choice == "3":
            if os.path.exists(HISTORY_FILE):
                confirmation = input(
                    "Удалить всю историю вычислений? (да/нет): "
                ).strip().lower()
                if confirmation in ("да", "y", "yes"):
                    os.remove(HISTORY_FILE)
                    print("История очищена.")
                else:
                    print("Отменено.")
            else:
                print("История и так пуста.")
            continue

        if choice == "1":
            a = get_number("Первое число: ")
            operator = input(
                "Операция (+, -, *, / или × для трёх чисел): "
            ).strip()
            b = get_number("Второе число: ")

            # Новая кнопка «×»: запрашиваем третье число
            c = None
            if needs_third_number(operator):
                c = get_number("Третье число: ")
                expression = f"{a:g} × {b:g} × {c:g}"
            else:
                expression = f"{a:g} {operator} {b:g}"

            try:
                result = calculate(a, operator, b, c)
            except (ZeroDivisionError, ValueError) as error:
                print(f"Ошибка: {error}")
                continue

            result_text = f"{result:g}"
            print(f"Результат: {expression} = {result_text}")
            save_calculation(expression, result_text)
            print("Вычисление сохранено в calculations.txt")
            continue

        print("Неизвестный пункт меню. Попробуйте снова.")

if __name__ == "__main__":
    main()
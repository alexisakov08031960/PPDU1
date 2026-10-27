history = []

while True:
    print("1. Сложение")
    print("2. Вычитание")
    print("3. Умножение")
    print("4. Деление")
    print("5. Просмотр истории")
    print("6. Выход")

    choice = input("Введите номер операции: ").strip()

    if choice == '6':
        print("До свидания!")
        break

    elif choice == '5':
        if not history:
            print("История пуста.")
        else:
            for i, record in enumerate(history, start=1):
                print(f"{i}. {record}")
        continue

    elif choice in ['1', '2', '3', '4']:
        try:
            a = float(input("Первое число: "))
            b = float(input("Второе число: "))
        except ValueError:
            print("Ошибка: введите число.")
            continue

        if choice == '1':
            result = a + b
            op = '+'
        elif choice == '2':
            result = a - b
            op = '-'
        elif choice == '3':
            result = a * b
            op = '*'
        else:
            if b == 0:
                print("Ошибка: деление на ноль.")
                continue
            result = a / b
            op = '/'

        record = f"{a} {op} {b} = {result}"
        history.append(record)
        print(record)

    else:
        print("Неверный пункт меню.")
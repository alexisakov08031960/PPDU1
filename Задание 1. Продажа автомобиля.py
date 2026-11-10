data = input("Введите параметры: ")

parts = data.split()

if len(parts) != 4:
    print("Ошибка: нужно ввести 4 параметра: модель, год, пробег, цена")
else:
    model, year, mileage, price = parts
    print(f"=== ПРОДАЖА АВТОМОБИЛЯ ===\n"
          f"Марка и модель: {model}\n"
          f"Год выпуска:   {year}\n"
          f"Пробег:        {mileage}\n"
          f"Цена:          {price}\n"
          f"===========================")
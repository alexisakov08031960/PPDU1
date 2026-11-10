data = input("Введите параметры: ")

model, year, mileage, price = data.split()

print(f"=== ПРОДАЖА АВТОМОБИЛЯ ===\n"
      f"Марка и модель: {model}\n"
      f"Год выпуска:   {year}\n"
      f"Пробег:        {mileage}\n"
      f"Цена:          {price}\n"
      f"===========================")
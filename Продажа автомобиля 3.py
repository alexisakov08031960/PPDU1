s = input("Введите данные: ")

brand, year, mileage, price = s.split()

print(
    f"Автомобиль: {brand}\n"
    f"Год выпуска: {year[:-1]}\n"
    f"Пробег: {mileage[:-2]}\n"
    f"Цена: {price[:-3]}"
)
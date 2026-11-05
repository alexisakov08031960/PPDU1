car = input("Введите данные автомобиля (например: LADA 2010г 205000км 450000руб): ")

brand, year, mileage, price = car.split()

print(f"Продажа автомобиля:\nМарка: {brand}\nГод выпуска: {year}\nПробег: {mileage}\nЦена: {price}")





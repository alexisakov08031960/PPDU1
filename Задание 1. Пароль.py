password = input("Введите пароль: ")

while len(password) < 8:
    print("Пароль должен содержать не менее 8 символов.")
    password = input("Попробуйте ещё раз: ")

print("Пароль принят.")
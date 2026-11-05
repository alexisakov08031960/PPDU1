MIN_LENGTH = 8

password = input("Введите пароль: ")

while len(password) < MIN_LENGTH:
    print(f"Слишком короткий пароль: {len(password)} симв. Нужно не менее {MIN_LENGTH}.")
    password = input("Введите пароль повторно: ")

print("Пароль принят.")
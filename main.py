def caesar(text, shift):
    """Сдвиг по коду символа с закольцовыванием в диапазоне Unicode."""
    return ''.join(chr((ord(c) + shift) % 0x110000) for c in text)

def main():
    while True:
        key = input('Введите ключ шифрования (целое число): ').strip()
        try:
            shift = int(key)
            break
        except ValueError:
            print('Ошибка: ключ должен быть целым числом. Попробуйте ещё раз.')

    try:
        with open('text.txt', 'r', encoding='utf-8') as f:
            s = f.read()
    except FileNotFoundError:
        print('Ошибка: файл "text.txt" не найден.')
        return

    secret = caesar(s, shift)

    with open('code.txt', 'w', encoding='utf-8') as f:
        f.write(secret)

    print('Текст зашифрован!')
    print('Файл "code.txt" для отправки сформирован.')

if __name__ == '__main__':
    main()
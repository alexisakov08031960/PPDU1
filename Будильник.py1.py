from tkinter import *
from tkinter import messagebox as mb
from time import strftime, localtime
import os

try:
    import pygame as pg
    pg.mixer.init()
    MUSIC_OK = True
    MUSIC_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'music.mp3')
    if os.path.exists(MUSIC_FILE):
        pg.mixer.music.load(MUSIC_FILE)
    else:
        MUSIC_OK = False
        print('Файл music.mp3 не найден — звук будильника отключён.')
except Exception as e:
    MUSIC_OK = False
    print(f'Звук недоступен: {e}')

def normalize_alarm(text: str):
    """Приводит ввод к 'HH:MM:SS' или 'HH:MM'. Возвращает None, если формат неверный."""
    text = text.strip().replace('.', ':').replace(' ', ':')
    parts = [p for p in text.split(':') if p != '']
    if not parts or len(parts) > 3:
        return None
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        return None
    if len(parts) == 1:                      # '9' -> '09:00:00'
        nums = [nums[0], 0, 0]
    elif len(parts) == 2:                    # '9:30' -> '09:30:00'
        nums = [nums[0], nums[1], 0]
    h, m, s = nums
    if not (0 <= h <= 23 and 0 <= m <= 59 and 0 <= s <= 59):
        return None
    return f'{h:02d}:{m:02d}:{s:02d}'

def tick():
    current_time = strftime('%H:%M:%S')
    screen_time.config(text=current_time)

    if time_alarm:
        # однократное срабатывание: сработало — сбрасываем
        if current_time >= time_alarm and not fired[0]:
            fired[0] = True
            play_music()

    # перепланирование с коррекцией дрейфа
    delay = 1000 - int(float(strftime('%S.%f' if False else '%S')))*0  # заглушка
    screen_time.after(200, tick)

def play_music():
    if MUSIC_OK:
        try:
            pg.mixer.music.play(-1)   # -1: повторять, пока не выключат
        except Exception as e:
            print(f'Не удалось проиграть музыку: {e}')
    mb.showinfo('Будильник', f'Сработал будильник на {time_alarm}')

def on_click():
    global time_alarm
    raw = entry_time.get().strip()
    alarm = normalize_alarm(raw)

    if alarm is None:
        mb.showerror('Ошибка', 'Неверный формат времени.\n'
                              'Примеры: 07:30, 7:30, 07:30:15, 7')
        return

    time_alarm = alarm
    fired[0] = False
    entry_time.delete(0, END)
    entry_time.insert(0, alarm[:5])
    mb.showinfo('Включение будильника', f'Будильник включён на {alarm[:5]}')

def off_click():
    global time_alarm
    time_alarm = ''
    fired[0] = False
    entry_time.delete(0, END)
    if MUSIC_OK:
        try:
            pg.mixer.music.stop()
        except Exception:
            pass
    mb.showinfo('Выключение будильника', 'Будильник выключен')

def on_close():
    global time_alarm
    time_alarm = ''
    try:
        if MUSIC_OK:
            pg.mixer.music.stop()
            pg.mixer.quit()
    finally:
        root.destroy()

# --- состояние ---
time_alarm = ''
fired = [False]

root = Tk()
root.title('Будильник')
root.config(background='black')
root.resizable(False, False)

WIN_W, WIN_H = 400, 210
SCREEN_W = root.winfo_screenwidth()
SCREEN_H = root.winfo_screenheight()
root.geometry(f'{WIN_W}x{WIN_H}+{(SCREEN_W - WIN_W) // 2}+{(SCREEN_H - WIN_H) // 2 - 25}')

screen_time = Label(root, text='00:00:00', font='Arial 50', bg='black', fg='lime')
screen_time.pack(pady=5)

entry_time = Entry(root, width=10, font='Arial 20', justify=CENTER)
entry_time.pack(pady=5)
entry_time.focus_set()

on = Button(root, text='Включить', font=('Arial', 10), command=on_click)
on.pack(pady=5)

off = Button(root, text='Выключить', font=('Arial', 10), command=off_click)
off.pack()

root.protocol('WM_DELETE_WINDOW', on_close)

tick()
root.mainloop()
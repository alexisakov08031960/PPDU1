from tkinter import *
import time
from tkinter import messagebox as mb

phrase = "quickbrownfox"

i = 0
t = time.time()

def start():
    global i, t
    i = 0
    t = time.time()
    label.config(text=phrase[i])
    window.bind("<Key>", check)

def check(event):
    global i

    # игнорируем служебные клавиши (Shift, Ctrl, стрелки и т.п.)
    if event.char == "":
        return

    if event.char == phrase[i]:
        i += 1
        if i == len(phrase):
            finish()
        else:
            label.config(text=phrase[i])
    else:
        label.config(
            text=f"Ошибка! Ожидалась буква '{phrase[i]}'.\n"
                 f"Нажмите любую клавишу для продолжения"
        )
        window.unbind("<Key>")
        window.bind("<Key>", cont)

def cont(event):
    global i
    label.config(text=phrase[i])
    window.unbind("<Key>")
    window.bind("<Key>", check)

def finish():
    window.unbind("<Key>")
    elapsed = time.time() - t
    time_allowed = len(phrase)

    if elapsed <= time_allowed:
        res = f"Вы победили! Ваше время {elapsed:.1f} сек."
    else:
        res = (f"Прошло {elapsed:.1f} сек. "
               f"Надо было уложиться в {time_allowed} сек.")

    label.config(text=res)
    mb.showinfo("Результат", res)

    if mb.askyesno("Повторить?", "Хотите повторить ещё раз?"):
        start()
    else:
        window.destroy()

window = Tk()
window.title("Клавиатурный тренажёр")
window.geometry("800x100")

label = Label(font=("Helvetica", 24))
label.pack()

start()
window.mainloop()
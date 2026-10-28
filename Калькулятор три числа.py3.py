import tkinter as tk
from tkinter import messagebox as mb

def summ():
    s1 = e1.get()
    if not s1.isdigit():
        mb.showerror("Ошибка", "В первое поле должно быть введено целое число")
        return
    s2 = e2.get()
    if not s2.isdigit():
        mb.showerror("Ошибка", "Во второе поле должно быть введено целое число")
        return
    slag_1 = int(s1)
    slag_2 = int(s2)
    summa = slag_1 + slag_2
    m1["text"] = f"{s1} + {s2} = {summa}"
    answer = mb.askyesno(title="Вопрос", message="Сложить ещё два числа?")
    if answer:
        e1.delete(0, tk.END)
        e2.delete(0, tk.END)
        m1["text"] = ""
    else:
        window.destroy()

def multiply_three():
    s1 = e1.get()
    s2 = e2.get()
    s3 = e3.get()
    if not (s1.isdigit() and s2.isdigit() and s3.isdigit()):
        mb.showerror("Ошибка", "В одно из полей должно быть введено целое число")
        return
    num1 = int(s1)
    num2 = int(s2)
    num3 = int(s3)
    result = num1 * num2 * num3
    m1["text"] = f"{num1} * {num2} * {num3} = {result}"
    answer = mb.askyesno(title="Вопрос", message="Умножить ещё три числа?")
    if answer:
        e1.delete(0, tk.END)
        e2.delete(0, tk.END)
        e3.delete(0, tk.END)
        m1["text"] = ""
    else:
        window.destroy()

window = tk.Tk()
window.title("Калькулятор")

m = tk.Label(window, height=3, text="Введите 3 целых числа и нажмите на кнопку умножения.")
m.pack()

e1 = tk.Entry(window)
e1.pack()
e2 = tk.Entry(window)
e2.pack()
e3 = tk.Entry(window)
e3.pack()

b_sum = tk.Button(text="Сложить два числа", command=summ)
b_sum.pack()

b_mult = tk.Button(text="Умножить три числа", command=multiply_three)
b_mult.pack()

m1 = tk.Label(window, height=3)
m1.pack()

window.mainloop()

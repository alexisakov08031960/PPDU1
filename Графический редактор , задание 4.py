import tkinter as tk
from tkinter import messagebox

current_color = "black"
brush_thickness = 2
last_x = last_y = None

def draw(event):
    global last_x, last_y
    if last_x is None:
        last_x, last_y = event.x, event.y
        return
    canvas.create_line(
        last_x, last_y, event.x, event.y,
        fill=current_color,
        width=brush_thickness * 2,
        capstyle=tk.ROUND,
        smooth=True,
    )
    last_x, last_y = event.x, event.y

def start_draw(event):
    global last_x, last_y
    last_x, last_y = event.x, event.y
    r = brush_thickness
    canvas.create_oval(
        event.x - r, event.y - r, event.x + r, event.y + r,
        fill=current_color, outline=current_color,
    )

def stop_draw(event):
    global last_x, last_y
    last_x = last_y = None

def change_color(new_color):
    global current_color
    current_color = new_color

def update_thickness():
    global brush_thickness
    try:
        thickness = int(thickness_entry.get())
    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректное целое число!")
        return

    if thickness <= 0:
        messagebox.showwarning("Внимание", "Толщина должна быть больше 0!")
        return

    brush_thickness = thickness

def clear_canvas():
    canvas.delete("all")

root = tk.Tk()
root.title("Графический редактор")

canvas = tk.Canvas(root, bg="white", width=600, height=400)
canvas.pack(fill=tk.BOTH, expand=True)

canvas.bind("<ButtonPress-1>", start_draw)
canvas.bind("<B1-Motion>", draw)
canvas.bind("<ButtonRelease-1>", stop_draw)

control_panel = tk.Frame(root, padx=10, pady=10)
control_panel.pack(side=tk.BOTTOM, fill=tk.X)

tk.Label(control_panel, text="Толщина:").pack(side=tk.LEFT, padx=5)

thickness_entry = tk.Entry(control_panel, width=5)
thickness_entry.insert(0, str(brush_thickness))
thickness_entry.pack(side=tk.LEFT, padx=5)

tk.Button(control_panel, text="Применить", command=update_thickness).pack(side=tk.LEFT, padx=5)
tk.Button(control_panel, text="Очистить", command=clear_canvas).pack(side=tk.LEFT, padx=5)

tk.Label(control_panel, text="Цвет:").pack(side=tk.LEFT, padx=(20, 5))

for color in ("green", "red", "blue", "black"):
    tk.Button(
        control_panel, bg=color, width=3,
        command=lambda c=color: change_color(c),
    ).pack(side=tk.LEFT, padx=2)

root.mainloop()
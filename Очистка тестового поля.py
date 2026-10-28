import tkinter as tk

root = tk.Tk()
root.title("Редактор")

menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Файл", menu=file_menu)

file_menu.add_command(label="Очистить", command=lambda: text.delete("1.0", tk.END))

file_menu.add_separator()
file_menu.add_command(label="Выход", command=root.destroy)

text = tk.Text(root, wrap="word", width=60, height=20)
text.pack(fill="both", expand=True)

root.mainloop()
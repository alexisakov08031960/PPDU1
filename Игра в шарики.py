import tkinter as tk

WIDTH, HEIGHT = 400, 300
STEP = 20
SIZE = 40


def move_ball(event):
    key = event.keysym
    x1, y1, x2, y2 = canvas.coords(ball)

    if key == "Up" and y1 > 0:
        canvas.move(ball, 0, -STEP)
    elif key == "Down" and y2 < HEIGHT:
        canvas.move(ball, 0, STEP)
    elif key == "Left" and x1 > 0:
        canvas.move(ball, -STEP, 0)
    elif key == "Right" and x2 < WIDTH:
        canvas.move(ball, STEP, 0)

    return "break"


window = tk.Tk()
window.title("Игра с шариком")
window.geometry(f"{WIDTH}x{HEIGHT}")
window.resizable(False, False)

canvas = tk.Canvas(window, width=WIDTH, height=HEIGHT, bg="white",
                   highlightthickness=0)
canvas.pack()

ball = canvas.create_oval(
    WIDTH // 2 - SIZE // 2, HEIGHT // 2 - SIZE // 2,
    WIDTH // 2 + SIZE // 2, HEIGHT // 2 + SIZE // 2,
    fill="red", outline="darkred"
)

for key in ("Up", "Down", "Left", "Right"):
    window.bind(f"<{key}>", move_ball)

window.mainloop()
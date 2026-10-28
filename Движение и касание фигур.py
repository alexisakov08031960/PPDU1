from tkinter import *


def move_ball(event):
    key = event.keysym
    x1, y1, x2, y2 = canvas.coords(ball)
    if key == 'Up' and y1 > 0:
        canvas.move(ball, 0, -20)
    elif key == 'Down' and y2 < 300:
        canvas.move(ball, 0, 20)
    elif key == "Left" and x1 > 0:
        canvas.move(ball, -20, 0)
    elif key == "Right" and x2 < 400:
        canvas.move( ball, 20, 0)

window = Tk()
window.title("Игра с шариком")
window.geometry("400x300")

import socket
import turtle

HOST = ("3.3.3.3", 5555)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(HOST)

screen = turtle.Screen()
screen.setup(600, 600)

t = turtle.Turtle('turtle')
t.speed(0)
t.color('blue')

STEP = 10

def send(cmd: str):
    sock.sendall((cmd + "\n").encode("utf-8"))

def move_up():
    t.setheading(90)
    t.forward(STEP)
    send("U")

def move_down():
    t.setheading(270)
    t.forward(STEP)
    send("D")

def move_left():
    t.setheading(180)
    t.forward(STEP)
    send("L")

def move_right():
    t.setheading(0)
    t.forward(STEP)
    send("R")

def quit_app():
    send("QUIT")
    try:
        sock.close()
    except Exception:
        pass
    screen.bye()

# Управление стрелками + выход по q
screen.onkey(move_up, "Up")
screen.onkey(move_down, "Down")
screen.onkey(move_left, "Left")
screen.onkey(move_right, "Right")
screen.onkey(quit_app, "q")

screen.listen()
screen.mainloop()
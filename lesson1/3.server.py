import socket
import threading
from queue import Queue
import turtle

HOST = ("0.0.0.0",5555)

# Очередь команд через кью
cmd_q = Queue()

# Turtle сделан в главном потоке
screen = turtle.Screen()
screen.setup(600, 600)

t = turtle.Turtle('turtle')
t.speed(0)
t.color('blue')

STEP = 10

def apply_command(cmd: str):
    if cmd == "U":
        t.setheading(90)
        t.forward(STEP)
    elif cmd == "D":
        t.setheading(270)
        t.forward(STEP)
    elif cmd == "L":
        t.setheading(180)
        t.forward(STEP)
    elif cmd == "R":
        t.setheading(0)
        t.forward(STEP)
    elif cmd == "QUIT":
        screen.bye()  # закрывает окно сервера

def tick():
    # Забираем все накопившиеся команды и применяем
    while not cmd_q.empty():
        cmd = cmd_q.get_nowait()
        apply_command(cmd)

    # Планируем следующий “тик” - сервер проверяет пришли ли команды
    screen.ontimer(tick, 20)

def net_worker(): #главный работяга по сети, чтобы не мешать с черепахой
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(HOST)
    sock.listen(1)

    print(f"Server listening on {HOST}")
    conn, addr = sock.accept()
    print("Client connected:", addr)

    f = conn.makefile("r", encoding="utf-8", newline="\n")
    for line in f:
        cmd = line.strip()
        if cmd:
            cmd_q.put(cmd)
        if cmd == "QUIT":
            break

    try:
        f.close()
    except Exception:
        pass
    conn.close()
    sock.close()

# Сеть — в отдельном потоке, turtle — в главном
threading.Thread(target=net_worker, daemon=True).start()

screen.ontimer(tick, 20)
screen.mainloop()
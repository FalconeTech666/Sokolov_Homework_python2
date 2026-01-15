'''
1. написать сервер на сокетах который может принимать 3 команды
    - time - отправляет обратно текущее время
    - rnd a:int b:int - отправляет обратно случайное число от а до b (пример - int 1 6)
    - stop - останавливает сервер - отправляет сообщение об этом
    - если прислана неизвестная  команда сообщить об этом клиенту
    
    * на сервере вести лог всех присланных команд в файл 
    
2. написать клиент который запрашивает бесконечно команду для сервера
    и выводит в консоль ответ.

'''

'''Сервер'''

import socket
import random
import logging
from datetime import datetime

HOST = ('61.18.2.4', 5555)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("server.log", encoding="utf-8")],
)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind(HOST)
sock.listen()

print('---start---')

running = True

while running:
    conn, addr = sock.accept()
    print(f'connected from {addr[0]}')

    f_in = conn.makefile("r", encoding="utf-8", newline="\n") # читаю сокет как файл и красиво скортирую информацию
    f_out = conn.makefile("w", encoding="utf-8", newline="\n") # запись

    while True:
        print('wait data')
        line = f_in.readline()
        if not line:
            break

        cmd = line.strip()
        if not cmd:
            continue

        # Логирую присланные комманды
        logging.info("%s:%s %s", addr[0], addr[1], cmd)

        parts = cmd.split()
        name = parts[0].lower()

        if name == "time" and len(parts) == 1:
            resp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        elif name == "rnd" and len(parts) == 3:
            try:
                a = int(parts[1])
                b = int(parts[2])
                if a > b:
                    a, b = b, a
                resp = str(random.randint(a, b))
            except ValueError:
                resp = "ERR: usage: rnd <int a> <int b>"

        elif name == "stop" and len(parts) == 1:
            resp = "OK: server stopping"
            f_out.write(resp + "\n")
            f_out.flush()
            running = False
            break

        else:
            resp = "ERR: unknown command"

        f_out.write(resp + "\n")
        f_out.flush()

    try:
        f_in.close()
        f_out.close()
    except Exception:
        pass

    conn.close()

sock.close()
print('---stop---')



'''Клиент'''

HOST = ('61.18.2.4', 5555)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(HOST)

while True:
    cmd = input(" ")           
    sock.sendall((cmd + "\n").encode("utf-8")) 
    data = sock.recv(1024)         
    if not data:               
        print("server closed connection")
        break
    print(data.decode("utf-8", errors="replace").strip())

sock.close() 
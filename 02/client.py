"""

написать приложение-клиент используя модуль socket работающее в домашней 
локальной сети.
Приложение должно соединятся с сервером по известному адрес:порт и отправлять 
туда текстовые данные.

известно что сервер принимает данные следующего формата:
    "command:reg; login:<login>; password:<pass>" - для регистрации пользователя
    "command:signin; login:<login>; password:<pass>" - для входа пользователя
    
    
с помощью программы зарегистрировать несколько пользователей на сервере и произвести вход


"""
### Без цикла и функций, просто накидывал для понимания
import socket

HOST = ("3.3.3.3", 5555)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(HOST)

sock.sendall('command:reg; login:user1; password:pass1').encode("utf-8")

sock.close()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(HOST)

sock.sendall('command:reg; login:user12; password:pass12').encode("utf-8")

sock.close()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(HOST)

sock.sendall('command:reg; login:user13; password:pass13').encode("utf-8")

sock.close()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(HOST)

sock.sendall('command:signin; login:user1; password:pass1').encode("utf-8")

sock.close()

### Нормальная версия 

def send_command(command, login, password):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(HOST)

    command_str = f"command:{command}; login:{login}; password:{password}"
    sock.sendall(command_str.encode("utf-8"))

    sock.close()

users = [
    ("user1", "pass1"),
    ("user2", "pass2"),
    ("user3", "pass3"),
]

for login, password in users:
    send_command("reg", login, password)

for login, password in users:
    send_command("signin", login, password)
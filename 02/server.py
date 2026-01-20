'''
написать приложение-сервер используя модуль socket работающее в домашней 
локальной сети.
Приложение должно принимать данные с любого устройства в сети отправленные 
или через программу клиент или через браузер
    - если данные пришли по протоколу http создать возможность след.логики:
        - если путь "/" - вывести главную страницу
        
        - если путь содержит /test/<int>/ вывести сообщение - тест с номером int запущен
                пример - 127.0.0.1:7777/test/1/
        
        - если путь содержит message/<login>/<text>/ вывести в консоль/браузер сообщение
            "{дата время} - сообщение от пользователя {login} - {text}"
        
        - если путь содержит указание на файл вывести в браузер этот файл
        
        - во всех остальных случаях вывести сообщение:
            "пришли неизвестные  данные по HTTP - путь такой то"
                   
         
    - если данные пришли НЕ по протоколу http создать возможность след.логики:
        - если пришла строка формата "command:reg; login:<login>; password:<pass>"
            - выполнить проверку:
                login - только латинские символы и цифры, минимум 6 символов
                password - минимум 8 символов, должны быть хоть 1 цифра
            - при успешной проверке:
                1. вывести сообщение на стороне клиента: 
                    "{дата время} - пользователь {login} зарегистрирован"
                2. добавить данные пользователя в список/словарь на сервере
            - если проверка не прошла вывести сообщение на стороне клиента:
                "{дата время} - ошибка регистрации {login} - неверный пароль/логин"
                
        - если пришла строка формата "command:signin; login:<login>; password:<pass>"
            выполнить проверку зарегистрирован ли такой пользователь на сервере:                
            
            при успешной проверке:
                1. вывести сообщение на стороне клиента: 
                    "{дата время} - пользователь {login} произведен вход"
                
            если проверка не прошла вывести сообщение на стороне клиента:
                "{дата время} - ошибка входа {login} - неверный пароль/логин"
        
        - во всех остальных случаях вывести сообщение на стороне клиента:
            "пришли неизвестные  данные - <присланные данные>"       
                 

'''


import socket

def send_file(file_name, conn):
    try:
        with open(file_name.lstrip('/'), 'rb') as f:                   
            print(f"send file {file_name}")
            conn.send(OK)
            conn.send(HEADERS)
            conn.send(f.read())
            
    except IOError:
        print('нет файла')
        conn.send(ERR_404)

def is_file(path):       
    if '.' in path:
        ext =  path.split(".")[-1]
        if ext in ['jpg','png','gif', 'ico', 'txt', 'html', 'json']:
            return True
    return False


def parse_command(line):
    parts = [p.strip() for p in line.split(';')]
    cmd_part = parts[0].split(':', 1)     
    login_part = parts[1].split(':', 1)   
    pass_part = parts[2].split(':', 1)    

    command = cmd_part[1]
    login = login_part[1]
    password = pass_part[1]
    return command, login, password

def valid_login(login: str) -> bool:
    return len(login) >= 6 and login.isalnum()

def valid_password(password: str) -> bool:
    return len(password) >= 8 and any(ch.isdigit() for ch in password)

HOST = ("0.0.0.0", 7777)  

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(HOST)
sock.listen()

print("----СТАРТ-----")


OK = b'HTTP/1.1 200 OK\n'
HEADERS = b"Host: some.ru\nHost1: some1.ru\nContent-Type: text/html; charset=utf-8\n\n"
ERR_404 = b'HTTP/1.1 404 Not Found\n\n'

users = {}

while 1:
    print('----------------- listen ------------------')
    conn, addr = sock.accept()

    try:
        data = conn.recv(4096)
        text = data.decode("utf-8", errors="ignore")
        print(text)

        first_line = text.split('\n', 1)[0].strip()

        if first_line.startswith('GET ') or first_line.startswith('POST '):
            method, path, ver = first_line.split(" ", 2)
            print('HTTP:', method, path, ver)

            if is_file(path):
                send_file(path, conn)

            else:
                if path == '/':
                    send_file('1.html', conn)

                elif path.startswith('/test/') and path.endswith('/'):
                    num_str = path[len('/test/'):-1]
                    if num_str.isdigit():
                        html = f"<h1>ТЕСТ {num_str} запущен</h1>"
                        conn.send(OK)
                        conn.send(HEADERS)
                        conn.send(html.encode())
                    else:
                        conn.send(ERR_404)

                elif path.startswith('/message/'):
                    parts = path.strip('/').split('/') 
                    if len(parts) >= 3:
                        login = parts[1]
                        text_msg = '/'.join(parts[2:])
                        
                        from datetime import datetime
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        msg = f"{now} - сообщение от пользователя {login} - {text_msg}"
                        print(msg)                     
                        
                        conn.send(OK)
                        conn.send(HEADERS)
                        conn.send(msg.encode('utf-8')) 
                    else:
                        conn.send(ERR_404)
                else:
                    msg = f"пришли неизвестные данные по HTTP - путь {path}"
                    conn.send(OK)
                    conn.send(HEADERS)
                    conn.send(msg.encode())
        else:
            line = text.strip()

            if line.startswith("command:reg"):
                cmd, login, password = parse_command(line)
                from datetime import datetime
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if valid_login(login) and valid_password(password):
                    users[login] = password
                    msg = f"{now} - пользователь {login} зарегистрирован"

                else:
                    msg = f"{now} - ошибка регистрации {login} - неверный пароль/логин"

                    conn.send(msg.encode('utf-8'))

            elif line.startswith("command:signin"):
                cmd, login, password = parse_command(line)
                from datetime import datetime
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if login in users and users[login] == password:
                    msg = f"{now} - пользователь {login} произведен вход"
                else:
                    msg = f"{now} - ошибка входа {login} - неверный пароль/логин"

                conn.send(msg.encode('utf-8'))
            else:
                print("NOT HTTP, unknown:", line)

    except Exception as e:
        print("ERROR:", e)

    conn.close()
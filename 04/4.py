'''
Добавить к прошлому проекту 2 страницы 
    - страницу с формой регистрации.
        Регистрация должна содержать имя фамилию возраст email логин пароль.
        После отправки формы регистрации проверить данные на валидность
            - имя фамилия - только русские буквы
            - логин - латинские цифры и _. От 6 до 20 символов
            - пароль - обязательно хотя бы 1 латинская маленькая, 1 заглавная и  1 цифр. От 8 до 15 символов.
            - * email - должен быть валидным
            - * возраст - целое число от 12 до 100
        При успешной проверке  добавить пользователя в базу/файл/список/словарь 
            и направить пользователя на форму входа.
        При выявлении ошибок снова показать форму, но уже с заполненными полями 
            и в любом месте формы показать список ошибок.
        
    - страницу с формой входа на сайт.
        - при успешном входе                             
            - пометить в сессиях что он залогинился
            - перенаправить на главную страницу
        - при ошибке показать форму снова, с сообщением об ошибке



Все прежние страницы сделать открытыми только для пользователей которые произвели вход на сайт.
Если пользователь не залогинился и переходит на них - перенаправлять его на форму входа. 
На фоме входа сделать ссылку на форму регистрации.

Если пользовался залогинился - на каждой странице сверху писать - "Приветствуем вас имя фамилия"

На главной странице показывать ссылку ВХОД и РЕГИСТРАЦИЯ для пользователей которые не вошли на сайт
и ссылку ВЫХОД для  пользователей которые вошли на сайт

Таким образом новый пользователь имеет доступ  только на главную страницу где есть ссылка на вход регистрацию.
После регистрации и входа он имеет доступ на все доступные страницы.

'''


from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import os
from random import randint
import requests
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import re


API_KEY = "c20b707c789771eddf22032f24f790ac"

BASE_DIR = os.path.dirname(__file__)

app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))

app.secret_key ="123456789"

USERS = {}

def validate_registration(form):
    errors = []
    clean_data = {}

    #Имя и фамилия
    first_name = (form.get("first_name") or "").strip()
    last_name = (form.get("last_name") or "").strip()

    name_pattern = r"^[А-Яа-яЁё]+$"

    if not first_name:
        errors.append("Имя обязательно для заполнения.")
    elif not re.match(name_pattern, first_name):
        errors.append("Имя должно содержать только русские буквы.")

    if not last_name:
        errors.append("Фамилия обязательна для заполнения.")
    elif not re.match(name_pattern, last_name):
        errors.append("Фамилия должна содержать только русские буквы.")

    clean_data["first_name"] = first_name
    clean_data["last_name"] = last_name

    #логин
    login = (form.get("login") or "").strip()
    login_pattern = r"^[A-Za-z0-9_]{6,20}$"

    if not login:
        errors.append("Логин обязателен для заполнения.")
    elif not re.match(login_pattern, login):
        errors.append("Логин может содержать латинские буквы, цифры и _, длиной от 6 до 20 символов.")
    elif login in USERS:
        errors.append("Пользователь с таким логином уже существует.")

    clean_data["login"] = login

    #пароль
    password = form.get("password") or ""

    if not password:
        errors.append("Пароль обязателен для заполнения.")
    else:
        if len(password) < 8 or len(password) > 15:
            errors.append("Пароль должен быть длиной от 8 до 15 символов.")
        if not re.search(r"[a-z]", password):
            errors.append("Пароль должен содержать хотя бы одну латинскую строчную букву.")
        if not re.search(r"[A-Z]", password):
            errors.append("Пароль должен содержать хотя бы одну латинскую заглавную букву.")
        if not re.search(r"[0-9]", password):
            errors.append("Пароль должен содержать хотя бы одну цифру.")

    if password and not any("Пароль" in e for e in errors):
        password_hash = generate_password_hash(password)
        clean_data["password_hash"] = password_hash

    #почта
    email = (form.get("email") or "").strip()
    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    if not email:
        errors.append("Email обязателен для заполнения.")
    elif not re.match(email_pattern, email):
        errors.append("Некорректный формат email.")

    clean_data["email"] = email

    #возраст
    age_raw = (form.get("age") or "").strip()

    try:
        age = int(age_raw)
        if age < 12 or age > 100:
            errors.append("Возраст должен быть от 12 до 100 лет.")
    except ValueError:
        errors.append("Возраст должен быть целым числом.")
        age = None

    clean_data["age"] = age

    return clean_data, errors

def get_current_user():
    login_value = session.get("user_login")
    if not login_value:
        return None
    return USERS.get(login_value)

def get_weather_for_city(city: str):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ru",
    }

    response = requests.get(url, params=params)
    data = response.json() 

    cod = data.get("cod")
    if cod != 200:
        return None, data.get("message", "Ошибка загрузки погоды")

    main = data["main"]
    weather = data["weather"][0]
    wind = data["wind"]


    dt = data["dt"]
    updated_at = datetime.fromtimestamp(dt).strftime("%d.%m.%Y %H:%M")

    icon = weather["icon"]
    icon_url = f"https://openweathermap.org/img/wn/{icon}@2x.png"

    forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
    forecast_response = requests.get(forecast_url, params=params)
    forecast_data = forecast_response.json()  
    forecast_days = []

    for item in forecast_data.get("list", [])[:4]:
        f_dt_txt = item["dt_txt"]          
        f_date = f_dt_txt[5:16]            
        f_main = item["main"]
        f_weather = item["weather"][0]

        f_temp = f_main["temp"]
        f_desc = f_weather["description"]
        f_icon = f_weather["icon"]
        f_icon_url = f"https://openweathermap.org/img/wn/{f_icon}.png"

        forecast_days.append({
            "date": f_date,
            "temp": f_temp,
            "description": f_desc,
            "icon_url": f_icon_url,
        })

    context = {
        "temp": main["temp"],
        "feels_like": main["feels_like"],
        "humidity": main["humidity"],
        "pressure": main["pressure"],
        "description": weather["description"],
        "wind_speed": wind["speed"],
        "updated_at": updated_at,
        "icon_url": icon_url,
        "forecast_days": forecast_days,
    }

    return context, None

@app.route("/register/", methods=["GET", "POST"])
def register():
    current_user = get_current_user()

    if request.method == "POST":
        clean_data, errors = validate_registration(request.form)

        if errors:
            return render_template(
                "register.html",
                errors=errors,
                form_data=request.form,
                user=current_user,
            )

        login = clean_data["login"]
        USERS[login] = {
            "first_name": clean_data["first_name"],
            "last_name": clean_data["last_name"],
            "age": clean_data["age"],
            "email": clean_data["email"],
            "password_hash": clean_data["password_hash"],
        }

        return redirect(url_for("login"))
    
    return render_template(
        "register.html",
        errors=[],
        form_data={},
        user=current_user,
    )

@app.route("/login/", methods=["GET", "POST"])
def login():
    current_user = get_current_user()

    errors = []

    if request.method == "POST":
        login_value = (request.form.get("login") or "").strip()
        password = request.form.get("password") or ""

        user = USERS.get(login_value)

        if user is None or not check_password_hash(user["password_hash"], password):
            errors.append("Неверный логин или пароль.")
            return render_template(
                "login.html",
                errors=errors,
                form_data=request.form,
                user=current_user,
            )

        session["user_login"] = login_value
        return redirect(url_for("index"))

    return render_template(
        "login.html",
        errors=errors,
        form_data={},
        user=current_user,
    )

@app.route("/logout/")
def logout():
    session.pop("user_login", None)
    return redirect(url_for("index"))

@app.route('/')
def index():
    current_user = get_current_user()
    return render_template("index.html", user=current_user)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')

@app.route('/duck/')
def duck():

    user = get_current_user()
    if user is None:
        return redirect(url_for("login"))
    
    duck_number = randint(1, 1000)
    
    res = requests.get("https://random-d.uk/api/random")
    data = res.json()
    image_url = data["url"]

    return render_template('duck.html'
                           ,duck_number=duck_number,
                           image_url=image_url,
                           user=user)

@app.route('/fox/<int:count>/')
def fox(count):

    user = get_current_user()
    if user is None:
        return redirect(url_for("login"))
    
    if count < 1 or count > 10:
        return render_template("fox_error.html", user=user)
    
    images = []

    for i in range(count):
        res = requests.get("https://randomfox.ca/floof/")
        data = res.json()
        images.append(data["image"])

    return render_template('fox.html',
                            count=count,
                            images=images,
                            user=user)

@app.route('/weather-minsk/')
def weather_minsk():

    user = get_current_user()
    if user is None:
        return redirect(url_for("login"))
    
    city_query = "Minsk,BY"
    context, error = get_weather_for_city(city_query)

    if error is not None:
        return render_template(
            "weather_error.html",
            city_display="Минск",
            error_message=error,
            user=user
        )

    return render_template(
        "weather.html",
        city_display="Минск",
        **context,
        user=user
    )

@app.route('/weather/<city>/')
def weather_city(city):

    user = get_current_user()
    if user is None:
        return redirect(url_for("login"))
    
    city_query = city 
    context, error = get_weather_for_city(city_query)

    if error is not None:
        return render_template(
            "weather_error.html",
            city_display=city,
            error_message=error,
            user=user
        )

    return render_template(
        "weather.html",
        city_display=city,
        **context,
        user=user
    )

app.run(host="0.0.0.0",port = 7777 ,debug=True)
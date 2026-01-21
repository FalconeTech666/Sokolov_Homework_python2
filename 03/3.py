'''

Написать веб-приложение на Flask со следующими ендпоинтами:
    - главная страница - содержит ссылки на все остальные страницы
    - /duck/ - отображает заголовок "рандомная утка №ххх" и картинка утки 
                которую получает по API https://random-d.uk/api/random
                
    - /fox/<int>/ - аналогично утке только с лисой (- https://randomfox.ca), 
                    но количество разных картинок определено int. 
                    если int больше 10 или меньше 1 - вывести сообщение 
                    что можно только от 1 до 10
    
    - /weather-minsk/ - показывает погоду в минске в красивом формате
    
    - /weather/<city>/ - показывает погоду в городе указанного в city
                    если такого города нет - написать об этом
    
    - по желанию добавить еще один ендпоинт на любую тему 
    
    
Добавить обработчик ошибки 404. (есть в example)
    

'''


from flask import Flask, jsonify, render_template
import os
from random import randint
import requests
from datetime import datetime

API_KEY = "c20b707c789771eddf22032f24f790ac"

BASE_DIR = os.path.dirname(__file__)

app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))

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


@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')

@app.route('/duck/')
def duck():
    duck_number = randint(1, 1000)
    
    res = requests.get("https://random-d.uk/api/random")
    data = res.json()
    image_url = data["url"]

    return render_template('duck.html'
                           ,duck_number=duck_number,
                           image_url=image_url)

@app.route('/fox/<int:count>/')
def fox(count):
    if count < 1 or count > 10:
        return render_template("fox_error.html")
    
    images = []

    for i in range(count):
        res = requests.get("https://randomfox.ca/floof/")
        data = res.json()
        images.append(data["image"])

    return render_template('fox.html',
                            count=count,
                            images=images)

@app.route('/weather-minsk/')
def weather_minsk():
    city_query = "Minsk,BY"
    context, error = get_weather_for_city(city_query)

    if error is not None:
        return render_template(
            "weather_error.html",
            city_display="Минск",
            error_message=error,
        )

    return render_template(
        "weather.html",
        city_display="Минск",
        **context,
    )

@app.route('/weather/<city>/')
def weather_city(city):
    city_query = city 
    context, error = get_weather_for_city(city_query)

    if error is not None:
        return render_template(
            "weather_error.html",
            city_display=city,
            error_message=error,
        )

    return render_template(
        "weather.html",
        city_display=city,
        **context,
    )

app.run(host="0.0.0.0",port = 7777 ,debug=True)
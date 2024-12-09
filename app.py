import requests
from flask import Flask, render_template, request

app = Flask(__name__)


def get_weather(lat, lon):
    API_KEY = "af26f54f-1383-4191-829e-5f6da0776a48"
    BASE_URL = "https://api.weather.yandex.ru/v2/forecast"
    try:
        headers = {"X-Yandex-API-Key": API_KEY}
        params = {"lat": lat, "lon": lon, "lang": "ru_RU"}
        response = requests.get(BASE_URL, headers=headers, params=params)
        if response.status_code != 200:
            return response.status_code
        weather_data = response.json()
        temperature = weather_data['fact']['temp']
        humidity = weather_data['fact']['humidity']
        wind_speed = weather_data['fact']['wind_speed']
        prec_prob = weather_data['fact']['prec_prob']
        result = {
            'temperature': temperature,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'prec_prob': prec_prob,
        }
        return result
    except Exception as e:
        return str(e)


def get_coordinates(name_city):
    API_KEY = "fbde1d79-63ea-4791-83dc-2cb9484623ca"
    BASE_URL = "https://geocode-maps.yandex.ru/1.x"
    params = {"apikey": API_KEY, "geocode": name_city, "format": "json"}
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        try:
            json_response = response.json()
            if json_response['response']['GeoObjectCollection']['featureMember']:
                point = json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point'][
                    'pos']
                lon, lat = point.split()
                return float(lat), float(lon)
        except ValueError:
            return "Ошибка при парсинге ответа от сервера."
    return f"Проблемы с сервером.{response.status_code}"


def check_good_weather(weather_data):
    if weather_data['temperature'] < 0 or weather_data['temperature'] > 35:
        return False
    if weather_data['wind_speed'] >= 13.89:
        return False
    if weather_data['prec_prob'] > 70:
        return False
    return True

@app.route('/', methods=['GET', 'POST'])
def home():
    warning_msg = None
    if request.method == 'POST':
        start_address = request.form.get('start_address')
        end_address = request.form.get('end_address')
        result = get_coordinates(start_address)
        start_lat, start_lon, end_lat, end_lon = None, None, None, None
        if type(result) == str:
            if (result == "Ошибка при парсинге ответа от сервера."):
                result += "Искренне извиняемся, разработчик скоро пофиксит баг!"
                render_template('index.html', error=result)
            else:
                res = result.split('.')
                if res[1] == '400':
                    return render_template('index.html', error="В запросе отсутствует обязательный параметр или указано неверное значение параметра. Проверьте правильность ввода!")
                elif res[1] == '403':
                    return render_template('index.html', error="Извините, но похоже наш Api ключ сломался")
                elif res[1] == '429':
                    return render_template('index.html', error="Извините, но мы достигли лимита запросов в секунду")
                else:
                    return render_template('index.html', error=f"{result} Проверьте правильность ввода!")
        else:
            start_lat, start_lon = result
        result = get_coordinates(end_address)
        if type(result) == str:
            if (result == "Ошибка при парсинге ответа от сервера."):
                result += "Искренне извиняемся, разработчик скоро пофиксит баг!"
                render_template('index.html', error=result)
            else:
                res = result.split('.')
                if res[1] == '400':
                    return render_template('index.html', error="В запросе отсутствует обязательный параметр или указано неверное значение параметра. Проверьте правильность ввода!")
                elif res[1] == '403':
                    return render_template('index.html', error="Извините, но похоже наш Api ключ сломался")
                elif res[1] == '429':
                    return render_template('index.html', error="Извините, но мы достигли лимита запросов в секунду")
                else:
                    return render_template('index.html', error=f"{result} Проверьте правильность ввода!")
        else:
            end_lat, end_lon = result
        if not start_lat or not start_lon or not end_lat or not end_lon:
            return render_template('index.html', error="Не удалось получить координаты для одного или обоих адресов.")
        start_weather = get_weather(start_lat, start_lon)
        if type(start_weather) == str:
            return render_template('index.html', error="Извините, но похоже, что разработчик допустил баги. Не волнуйтесь, скоро пофиксим.")
        elif type(start_weather) == int:
            if start_weather == 400:
                return render_template('index.html', error="Ошибка запроса или пустой ответ от API. Проверьте правильность ввода!")
            elif start_weather == 403:
                return render_template('index.html', error="Извините, но похоже наш Api ключ сломался")
            elif start_weather == 429:
                return render_template('index.html', error="Извините, но мы достигли лимита запросов в секунду")
            else:
                return render_template('index.html', error=f"{start_weather} Ошибка сервера")
        end_weather = get_weather(end_lat, end_lon)
        if type(end_weather) == str:
            return render_template('index.html', error="Извините, но похоже, что разработчик допустил баги. Не волнуйтесь, скоро пофиксим.")
        elif type(end_weather) == int:
            if end_weather == 400:
                return render_template('index.html', error="Ошибка запроса или пустой ответ от API. Проверьте правильность ввода!")
            elif end_weather == 403:
                return render_template('index.html', error="Извините, но похоже наш Api ключ сломался")
            elif end_weather == 429:
                return render_template('index.html', error="Извините, но мы достигли лимита запросов в секунду")
            else:
                return render_template('index.html', error=f"{end_weather} Ошибка сервера")

        start_weather['good_weather'] = check_good_weather(start_weather)
        end_weather['good_weather'] = check_good_weather(end_weather)

        if not start_weather['good_weather'] or not end_weather['good_weather']:
            warning_msg = "Предупреждение! Погода в одном из городов плохая."
        else:
            warning_msg = "Погода в обоих городах хорошая. Счастливого пути!"

        weather = {
            "start_address": start_weather,
            "end_address": end_weather,
        }

        return render_template('index.html', weather=weather, warning_msg=warning_msg, start_address=start_address,
                               end_address=end_address)

    return render_template('index.html', warning_msg=warning_msg)


if __name__ == '__main__':
    app.run(debug=True)

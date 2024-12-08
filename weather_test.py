import requests

API_KEY = "af26f54f-1383-4191-829e-5f6da0776a48"
BASE_URL = "https://api.weather.yandex.ru/v2/forecast"


def get_weather(lat, lon):
    try:
        headers = {"X-Yandex-API-Key": API_KEY}
        params = {"lat": lat, "lon": lon, "lang": "ru_RU"}
        response = requests.get(BASE_URL, headers=headers, params=params)
        if response.status_code != 200:
            print(f"{response.status_code} проверьте ключ или доступность сервиса")
            raise
        weather_data = response.json()
        #Я сохранял json файл, чтобы изучить его структуру
        #with open('weather_data.json', 'w') as file:
        #    json.dump(weather_data, file, ensure_ascii=False, indent=4)
        temperature = weather_data['fact']['temp']
        humidity = weather_data['fact']['humidity']
        wind_speed = weather_data['fact']['wind_speed']
        prec_prob = weather_data['fact']['prec_prob']
        #print(temperature, humidity, wind_speed, prec_prob)
        result = {
            'temperature': temperature,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'prec_prob': prec_prob,
        }
        return result
    except Exception as e:
        return {"error": str(e)}

'''
У меня плохой уровень Англиского, поэтому я решил использовать Яндекс погоду.
+ надо поддерживать отечественного производителя.

latitude = 55.7558
longitude = 37.6173
weather = get_weather(latitude, longitude)
print(weather)#Проверили погоду в Москве
latitude = 56.878396
longitude = 53.267074
weather = get_weather(latitude, longitude)
print(weather)#Проверили погоду в Ижевске
latitude = 43.401075
longitude = 39.965027
weather = get_weather(latitude, longitude)
print(weather)#Проверили погоду в Сочи
'''
#Запросы работают корректно, все файн
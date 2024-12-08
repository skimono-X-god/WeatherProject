from weather_test import get_weather
def check_good_weather(weather_data):
    if weather_data['temperature'] < 0 or weather_data['temperature'] > 35:
        return False
    if weather_data['wind_speed'] >= 13.89:
        return False
    if weather_data['prec_prob'] > 70:
        return False
    return True

'''
Будем проверять, используя запросы из городов, которые мы брали для weather_test.py
Фунцкия возвращает True, если погода хорошая и False, если плохая
'''

latitude = 55.7558
longitude = 37.6173
weather = get_weather(latitude, longitude)
print(check_good_weather(weather))#Проверили погоду в Москве
latitude = 56.878396
longitude = 53.267074
weather = get_weather(latitude, longitude)
print(check_good_weather(weather))#Проверили погоду в Ижевске
latitude = 43.401075
longitude = 39.965027
weather = get_weather(latitude, longitude)
print(check_good_weather(weather))#Проверили погоду в Сочи
'''
Все правильно обработалось, занесем в Github
'''
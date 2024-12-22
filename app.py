import requests
import folium
from flask import Flask, render_template, request
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objs as go

app = Flask(__name__)

dash_app = Dash(__name__, server=app, url_base_pathname='/dash/')
weather_data = {}


def get_weather(lat, lon, days):
    API_KEY = "7c5ea75c-f294-4003-9b98-7dff2c45e57c"
    BASE_URL = "https://api.weather.yandex.ru/v2/forecast"

    try:
        headers = {"X-Yandex-API-Key": API_KEY}
        params = {
            "lat": lat,
            "lon": lon,
            "lang": "ru_RU",
            "limit": days
        }

        response = requests.get(BASE_URL, headers=headers, params=params)

        if response.status_code != 200:
            return f"Ошибка API: {response.status_code}"

        weather_data = response.json()
        forecasts = []
        for forecast in weather_data['forecasts']:
            day_weather = {
                'date': forecast['date'],
                'temperature': forecast['parts']['day']['temp_max'],
                'humidity': forecast['parts']['day']['humidity'],
                'wind_speed': forecast['parts']['day']['wind_speed'],
                'prec_prob': forecast['parts']['day']['prec_prob']
            }
            forecasts.append(day_weather)

        return forecasts

    except Exception as e:
        return f"Извините, произошла ошибка: {e}"


def get_coordinates(name_city):
    API_KEY = "fbde1d79-63ea-4791-83dc-2cb9484623ca"
    BASE_URL = "https://geocode-maps.yandex.ru/1.x"
    params = {"apikey": API_KEY, "geocode": name_city, "format": "json"}
    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        json_response = response.json()
        if json_response['response']['GeoObjectCollection']['featureMember']:
            point = json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
            lon, lat = point.split()
            return float(lat), float(lon)
    return None


@app.route('/', methods=['GET', 'POST'])
def home():
    global weather_data
    warning_msg = None
    intermediate_addresses = []

    if request.method == 'POST':
        start_address = request.form.get('start_address')
        end_address = request.form.get('end_address')
        intermediate_addresses = request.form.getlist('intermediate_addresses')
        days = request.form.get('days')

        start_coords = get_coordinates(start_address)
        if start_coords is None:
            return render_template('index.html', error=f"Не удалось получить координаты для '{start_address}'")

        start_lat, start_lon = start_coords

        end_coords = get_coordinates(end_address)
        if end_coords is None:
            return render_template('index.html', error=f"Не удалось получить координаты для '{end_address}'")

        end_lat, end_lon = end_coords

        addresses = {
            start_address: (start_lat, start_lon),
        }

        for addr in intermediate_addresses:
            addr = addr.strip()
            if addr:
                result = get_coordinates(addr)
                if result is None:
                    return render_template('index.html', error=f"Не удалось получить координаты для '{addr}'")
                addresses[addr] = result

        addresses[end_address] = (end_lat, end_lon)

        weather_data = {}
        for key, (lat, lon) in addresses.items():
            weather = get_weather(lat, lon, days)
            if isinstance(weather, str):
                return render_template('index.html', error=weather)
            weather_data[key] = weather

        warning_msg = "Погода получена успешно."

        my_map = folium.Map(location=[start_lat, start_lon], zoom_start=5)

        folium.Marker([start_lat, start_lon], tooltip=start_address, popup=f'{start_address}').add_to(my_map)

        for addr, (lat, lon) in addresses.items():
            folium.Marker([lat, lon], tooltip=addr,
                          popup=f'{addr}<br>Температура: {weather_data[addr][0]["temperature"]}°C<br>Влажность: {weather_data[addr][0]["humidity"]}%').add_to(
                my_map)

        coords = list(addresses.values())

        folium.PolyLine(locations=coords, color='blue').add_to(my_map)

        my_map.save('templates/map.html')

        return render_template('index.html', start_address=start_address, end_address=end_address,
                               intermediate_addresses=intermediate_addresses, weather=weather_data,
                               warning_msg=warning_msg)

    return render_template('index.html', warning_msg=warning_msg)

dash_app.layout = html.Div([
    dcc.Dropdown(
        id='parameter-dropdown',
        options=[
            {'label': 'Температура', 'value': 'temperature'},
            {'label': 'Скорость ветра', 'value': 'wind_speed'},
            {'label': 'Вероятность осадков', 'value': 'prec_prob'},
            {'label': 'Влажность', 'value': 'humidity'},
        ],
        value='temperature',
        multi=False
    ),
    dcc.Graph(id='weather-graph'),
])


@dash_app.callback(
    Output('weather-graph', 'figure'),
    Input('parameter-dropdown', 'value')
)
def update_graph(selected_parameter):
    traces = []
    for key, forecasts in weather_data.items():
        x_values = [forecast['date'] for forecast in forecasts]
        y_values = [forecast[selected_parameter] for forecast in forecasts]

        traces.append(go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines+markers',
            name=key
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            title='Прогноз погоды',
            xaxis=dict(title='Дата'),
            yaxis=dict(title=selected_parameter.capitalize()),
            hovermode='closest'
        )
    }


@app.route('/map')
def map_view():
    return render_template('map.html')


if __name__ == '__main__':
    app.run(debug=True)

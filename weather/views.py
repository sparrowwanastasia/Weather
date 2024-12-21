import requests
from django.shortcuts import render
from .models import City
from django.http import JsonResponse
from django.core.serializers import serialize
from urllib.parse import quote

# Используйте ваш ключ API
API_URL = 'http://api.openweathermap.org/data/2.5/weather?q={}&units={}&appid=a825c8d4a066459585b36363c2cb0245'
FORECAST_API_URL = 'http://api.openweathermap.org/data/2.5/forecast?q={}&units={}&appid=a825c8d4a066459585b36363c2cb0245'

def get_weather_and_forecast(request):
    cities = City.objects.all().values()
    cities_list = [{'id': city['id'], 'name': city['name']} for city in cities]

    if request.method == 'POST':
        city_name = request.POST.get('city')
        unit = request.POST.get('unit')
        unit_type = 'metric' if unit == 'celsius' else 'imperial'
        
        city_name_encoded = quote(city_name)
        
        # Получаем текущую погоду
        response = requests.get(API_URL.format(city_name_encoded, unit_type))
        if response.status_code == 200:
            weather_data = response.json()
            City.objects.get_or_create(name=city_name)
            
            # Получаем прогноз погоды
            forecast_response = requests.get(FORECAST_API_URL.format(city_name_encoded, unit_type))
            if forecast_response.status_code == 200:
                forecast_data = forecast_response.json()
                forecast_list = []

                for forecast in forecast_data['list']:
                    forecast_data_cleaned = {
                        'date': forecast['dt_txt'],
                        'temperature': forecast['main']['temp'],
                        'weather': forecast['weather'][0]['description'],
                        'humidity': forecast['main']['humidity'],
                        'wind_speed': forecast['wind']['speed']
                    }
                    forecast_list.append(forecast_data_cleaned)

                # Получаем URL изображения текущей погоды
                weather_icon_code = weather_data['weather'][0]['icon']  # Получаем код иконки
                weather_image_url = f'http://openweathermap.org/img/wn/{weather_icon_code}.png'  # Формируем URL изображения

                context = {
                    'cities': cities_list,
                    'city': city_name,  # Добавьте это
                    'temperature': weather_data['main']['temp'],
                    'weather': weather_data['weather'][0]['description'],
                    'humidity': weather_data['main']['humidity'],
                    'pressure': weather_data['main']['pressure'],
                    'wind_speed': weather_data['wind']['speed'],
                    'forecast': forecast_list,
                    'weather_image_url': weather_image_url  # Добавляем URL изображения
                }

                return JsonResponse(context)
            else:
                return JsonResponse({'error': 'Не удалось получить прогноз погоды!'}, status=404)
        else:
            return JsonResponse({'error': 'Город не найден!'}, status=404)

    return render(request, 'weather/index.html', {'cities': cities_list})
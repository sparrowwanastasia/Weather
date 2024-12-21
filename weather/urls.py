from django.urls import path
from .views import get_weather_and_forecast

urlpatterns = [
    path('', get_weather_and_forecast, name='get_weather_and_forecast'),
]
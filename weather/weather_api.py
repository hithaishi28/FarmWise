import os
import requests
from dotenv import load_dotenv

# Load .env from the project root
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
GEOCODING_URL = "https://api.openweathermap.org/geo/1.0/direct"


def check_api_key():
    """Check whether the OpenWeather API key exists."""
    if not API_KEY:
        return {
            "error": "OPENWEATHER_API_KEY is missing from the .env file."
        }

    return None


def get_coordinates(city):
    """Get latitude and longitude for a city."""

    key_error = check_api_key()
    if key_error:
        return key_error

    params = {
        "q": city,
        "limit": 1,
        "appid": API_KEY
    }

    try:
        response = requests.get(
            GEOCODING_URL,
            params=params,
            timeout=10
        )
    except requests.RequestException as error:
        return {"error": f"Geocoding request failed: {error}"}

    if response.status_code != 200:
        try:
            error_message = response.json().get(
                "message",
                "Geocoding API error"
            )
        except ValueError:
            error_message = "Geocoding API error"

        return {
            "error": error_message,
            "status_code": response.status_code
        }

    data = response.json()

    if not data:
        return {"error": "City not found"}

    return {
        "city": data[0]["name"],
        "country": data[0].get("country"),
        "latitude": data[0]["lat"],
        "longitude": data[0]["lon"]
    }


def get_weather(city):
    """Get current weather for a city."""

    key_error = check_api_key()
    if key_error:
        return key_error

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(
            BASE_URL,
            params=params,
            timeout=10
        )
    except requests.RequestException as error:
        return {"error": f"Weather request failed: {error}"}

    if response.status_code != 200:
        try:
            error_message = response.json().get(
                "message",
                "Weather API error"
            )
        except ValueError:
            error_message = "Weather API error"

        return {
            "error": error_message,
            "status_code": response.status_code
        }

    data = response.json()

    weather = {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "wind_speed": data["wind"]["speed"],
        "clouds": data["clouds"]["all"],
        "description": data["weather"][0]["description"],
        "sunrise": data["sys"]["sunrise"],
        "sunset": data["sys"]["sunset"]
    }

    return weather


def get_forecast(latitude, longitude):
    """Get 5-day / 3-hour weather forecast."""

    key_error = check_api_key()
    if key_error:
        return key_error

    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(
            FORECAST_URL,
            params=params,
            timeout=10
        )
    except requests.RequestException as error:
        return {"error": f"Forecast request failed: {error}"}

    if response.status_code != 200:
        try:
            error_message = response.json().get(
                "message",
                "Forecast API error"
            )
        except ValueError:
            error_message = "Forecast API error"

        return {
            "error": error_message,
            "status_code": response.status_code
        }

    return response.json()


def format_forecast(forecast_data):
    """Convert OpenWeather forecast into a simpler format."""

    if "error" in forecast_data:
        return forecast_data

    formatted = []

    for item in forecast_data["list"]:
        formatted.append({
            "datetime": item["dt_txt"],
            "temperature": item["main"]["temp"],
            "humidity": item["main"]["humidity"],
            "wind_speed": item["wind"]["speed"],
            "description": item["weather"][0]["description"],
            "rain_probability": item.get("pop", 0) * 100
        })

    return formatted


def get_weather_data(city):
    """Get location, current weather and forecast."""

    location = get_coordinates(city)

    if "error" in location:
        return location

    current_weather = get_weather(city)

    if "error" in current_weather:
        return current_weather

    forecast_data = get_forecast(
        location["latitude"],
        location["longitude"]
    )

    if "error" in forecast_data:
        return forecast_data

    forecast = format_forecast(forecast_data)

    return {
        "location": location,
        "current": current_weather,
        "forecast": forecast
    }


if __name__ == "__main__":
    print("Testing OpenWeather API...")

    data = get_weather_data("Bangalore")

    print(data)
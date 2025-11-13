"""
Weather Data Collector Module
Fetches weather data from various APIs based on GPS location
"""

import requests
import yaml
from datetime import datetime, timedelta
from typing import Dict, Optional
import json


class WeatherDataCollector:
    """Collects weather data from external APIs"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize collector with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.lat = self.config['location']['latitude']
        self.lon = self.config['location']['longitude']
        self.api_key = self.config['weather_api']['api_key']
        self.provider = self.config['weather_api']['provider']

    def collect_current_weather(self) -> Optional[Dict]:
        """Collect current weather data"""
        if self.provider == "openweathermap":
            return self._fetch_openweathermap()
        else:
            raise ValueError(f"Unsupported weather provider: {self.provider}")

    def _fetch_openweathermap(self) -> Optional[Dict]:
        """Fetch data from OpenWeatherMap API"""
        try:
            # Current weather
            current_url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': self.lat,
                'lon': self.lon,
                'appid': self.api_key,
                'units': 'imperial'  # Fahrenheit
            }

            response = requests.get(current_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Calculate wind chill
            temp_f = data['main']['temp']
            wind_speed_mph = data['wind']['speed']
            wind_chill = self._calculate_wind_chill(temp_f, wind_speed_mph)

            # Extract relevant data
            weather_data = {
                'timestamp': datetime.now().isoformat(),
                'temperature_f': temp_f,
                'feels_like_f': data['main']['feels_like'],
                'wind_chill_f': wind_chill,
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed_mph': wind_speed_mph,
                'wind_direction_deg': data['wind'].get('deg', 0),
                'wind_gust_mph': data['wind'].get('gust', wind_speed_mph),
                'weather_condition': data['weather'][0]['main'],
                'weather_description': data['weather'][0]['description'],
                'clouds_percent': data['clouds']['all'],
                'visibility_meters': data.get('visibility', 10000),
                'rain_1h_mm': data.get('rain', {}).get('1h', 0),
                'snow_1h_mm': data.get('snow', {}).get('1h', 0),
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).isoformat(),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']).isoformat(),
            }

            return weather_data

        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None
        except KeyError as e:
            print(f"Error parsing weather data: {e}")
            return None

    def _calculate_wind_chill(self, temp_f: float, wind_speed_mph: float) -> float:
        """
        Calculate wind chill temperature using NWS formula
        Valid for temps <= 50°F and wind speeds >= 3 mph
        """
        if temp_f > 50 or wind_speed_mph < 3:
            return temp_f

        wind_chill = (35.74 +
                     0.6215 * temp_f -
                     35.75 * (wind_speed_mph ** 0.16) +
                     0.4275 * temp_f * (wind_speed_mph ** 0.16))

        return round(wind_chill, 2)

    def get_wind_direction_name(self, degrees: float) -> str:
        """Convert wind direction in degrees to cardinal direction"""
        directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                     'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        index = round(degrees / 22.5) % 16
        return directions[index]

    def is_daytime(self, timestamp: str, sunrise: str, sunset: str) -> bool:
        """Check if timestamp is during daytime"""
        ts = datetime.fromisoformat(timestamp)
        sr = datetime.fromisoformat(sunrise)
        ss = datetime.fromisoformat(sunset)
        return sr <= ts <= ss


if __name__ == "__main__":
    # Test the collector
    collector = WeatherDataCollector()
    weather = collector.collect_current_weather()

    if weather:
        print("Current Weather Data:")
        print(json.dumps(weather, indent=2))
        print(f"\nWind Direction: {collector.get_wind_direction_name(weather['wind_direction_deg'])}")
        print(f"Is Daytime: {collector.is_daytime(weather['timestamp'], weather['sunrise'], weather['sunset'])}")

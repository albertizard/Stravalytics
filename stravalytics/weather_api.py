from dotenv import load_dotenv
import os
import json
from stravalytics.api_utils import ApiUtils 


class WeatherApiClient(ApiUtils):
    """
    Uses weatherapi.com, a weather API, to retrieve weather data.
    Can produce a summary of the weather conditions and add an emoji.    
    """

    def __init__(self, lat, lon, date, hour):
        """
        Set coordinates, date and time.
        Get WeatherApi key from .env.
        """
        
        self.lat = lat
        self.lon = lon
        self.date = date
        self.hour = hour

        self.weather_data = None
        self.weather_summary = None
        self.weather_emoji = None

        # Load .env file
        load_dotenv()

        # Read environment variables
        self.api_key = os.getenv('WEATHERAPI_KEY')

    
    def get_weatherapi_url(self):
        """
        Build a weatherapi url.
        See www.weatherapi.com/docs
        """
        url = (
            f'http://api.weatherapi.com/v1/history.json?'
            f'key={self.api_key}'
            f'&q={self.lat},{self.lon}'
            f'&dt={self.date}&hour={self.hour}'
        )
        return url
        
    
    def get_weather_data(self):
        """
        Call the weather api to get the weather data
        """
        
        url = self.get_weatherapi_url()
        
        weather_data = self.api_call('GET', url)

        if weather_data is not None:
            weather_data = weather_data['forecast']['forecastday'][0]['hour'][0]

        self.weather_data = weather_data

    
    @staticmethod
    def degrees_to_cardinal(d):
        """
        Convert the wind direction in degrees to a cardinal direction.
        """
        
        dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        ix = int((d + 11.25) / 22.5)
        return dirs[ix % 16]

    
    def format_weather_summary(self):
        """
        Take weather data and produce a weather summary and emoji.
        """

        w = self.weather_data
        
        if w is None:
            print("Weather data is empty, no weather summary was produced.")
            return None
        else:
            day_or_night = 'day'*(w['is_day']==1) + 'night'*(w['is_day']==0)

            emojis = WeatherEmojis.get_emojis_dict()
            emoji = emojis[w['condition']['text']][day_or_night]["emoji_unicode"]
            
            summary = f"{emoji} " \
                    + f"{w['condition']['text']}," \
                    + f" {w['temp_c']}\u00b0C," \
                    + f" humidity {w['humidity']}%," \
                    + f" wind {w['wind_kph']} km/h" \
                    + f" from {(w['wind_dir'])}" \
                    # + f" from {degrees_to_cardinal(w['wind_degree'])}"
            
            self.weather_summary = summary
            self.weather_emoji = emoji
            # return summary, emoji


class WeatherEmojis():
    """
    Utilities to build a mapping between weather emojis (and their
    unicode values) and weather conditions (and a time of the day).
    """

    @staticmethod
    def get_emojis_dict():
        """
        Returns dictionary relating:
            - weather condition
                - Time of day (day/night)
                    - Emoji character
                    - Emoji in unicode 
        Mapping written manually (with help of NLPs).
        """
    
        emojis_dict = {
            "Sunny": {
                "day": {"emoji": "☀️", "emoji_unicode": "\u2600"},
            },
            "Clear": {
                "night": {"emoji": "🌙", "emoji_unicode": "\U0001F319"},
            },
            "Partly Cloudy": {
                "day": {"emoji": "🌤️", "emoji_unicode": "\U0001F324"},
                "night": {"emoji": "🌙☁️", "emoji_unicode": "\U0001F319\u2601"}
            },
            "Cloudy": {
                "day": {"emoji": "☁️", "emoji_unicode": "\u2601"},
                "night": {"emoji": "☁️", "emoji_unicode": "\u2601"}
            },
            "Overcast": {
                "day": {"emoji": "☁️", "emoji_unicode": "\u2601"},
                "night": {"emoji": "☁️", "emoji_unicode": "\u2601"}
            },
            "Mist": {
                "day": {"emoji": "🌫️", "emoji_unicode": "\U0001F32B"},
                "night": {"emoji": "🌫️", "emoji_unicode": "\U0001F32B"}
            },
            "Patchy rain nearby": {
                "day": {"emoji": "🌦️", "emoji_unicode": "\U0001F326"},
                "night": {"emoji": "🌧️", "emoji_unicode": "\U0001F327"}
            },
            "Patchy snow nearby": {
                "day": {"emoji": "🌨️", "emoji_unicode": "\U0001F328"},
                "night": {"emoji": "🌨️", "emoji_unicode": "\U0001F328"}
            },
            "Patchy sleet nearby": {
                "day": {"emoji": "🌧️", "emoji_unicode": "\U0001F327"},
                "night": {"emoji": "🌧️", "emoji_unicode": "\U0001F327"}
            },
            "Patchy freezing drizzle nearby": {
                "day": {"emoji": "🌧️", "emoji_unicode": "\U0001F328"},
                "night": {"emoji": "🌧️", "emoji_unicode": "\U0001F328"}
            },
            "Thundery outbreaks in nearby": {
                "day": {"emoji": "⛈️", "emoji_unicode": "\U000026C8"},
                "night": {"emoji": "⛈️", "emoji_unicode": "\U000026C8"}
            },
            "Blowing snow": {
                "day": {"emoji": "🌨️", "emoji_unicode": "\U0001F328"},
                "night": {"emoji": "🌨️", "emoji_unicode": "\U0001F328"}
            },
            "Blizzard": {
                "day": {"emoji": "🌨️", "emoji_unicode": "\U0001F328"},
                "night": {"emoji": "🌨️", "emoji_unicode": "\U0001F328"}
            },
            "Fog": {
                "day": {"emoji": "🌫️", "emoji_unicode": "\U0001F32B"},
                "night": {"emoji": "🌫️", "emoji_unicode": "\U0001F32B"}
            },
            "Freezing fog": {
                "day": {"emoji": "🌫️", "emoji_unicode": "\U0001F32B"},
                "night": {"emoji": "🌫️", "emoji_unicode": "\U0001F32B"}
            },
            "Patchy light drizzle": {
                "day": {"emoji": "🌦️", "emoji_unicode": "\U0001F326"},
                "night": {"emoji": "🌧️", "emoji_unicode": "\U0001F327"}
            },
            "Light drizzle": {
                "day": {"emoji": "🌦️", "emoji_unicode": "\U0001F326"},
                "night": {"emoji": "🌧️", "emoji_unicode": "\U0001F327"}
            },
            "Freezing drizzle": {
                "day": {"emoji": "🌧️", "emoji_unicode": "\U0001F327"},
                "night": {"emoji": "🌧️", "emoji_unicode": "\U0001F327"}
            },
            "Heavy freezing drizzle": {
                "day": {"emoji": "🌧️", "emoji_unicode": "\U0001F327"},
                "night": {"emoji": "🌧️", "emoji_unicode": "\U0001F327"}
            },
            "Patchy light rain": {
                "day": {"emoji": "🌦️", "emoji_unicode": "\U0001F326"},
                "night": {"emoji": "🌧️", "emoji_unicode": "\U0001F327"}
            },
            "Light rain": {
                "day": {"emoji": "🌦️", "emoji_unicode": "\U0001F326"},
                "night": {"emoji": "🌧️", "emoji_unicode": "\U0001F327"}
            },
            "Moderate rain at times": {
                "day": {"emoji": "🌧️", "emoji_unicode": "\U0001F327"},
                "night": {"emoji": "🌧️", "emoji_unicode": "\U0001f327"}
            },
            "Moderate rain": {
                "day": {"emoji": "🌧️", "emoji_unicode": "\U0001f327"},
                "night": {"emoji": "🌧️", "emoji_unicode": "\U0001f327"}
            },
            "Heavy rain at times": {
                "day": {"emoji": "🌧️", "emoji_unicode": "\U0001f327"},
                "night": {"emoji": "🌧️", "emoji_unicode": "\U0001f327"}
            },
            "Heavy rain": {
                "day": {"emoji": "🌧️", "emoji_unicode": "\U0001f327"},
                "night": {"emoji": "🌧️", "emoji_unicode": "\U0001f327"}
            },
            "Light freezing rain": {
                "day": {"emoji": "🌧️", "emoji_unicode": "\U0001f327"},
                "night": {"emoji": "🌧️", "emoji_unicode": "\U0001f327"}
            },
            "Moderate or heavy freezing rain": {
                "day": {"emoji": "🌧️", "emoji_unicode": "\U0001f327"},
                "night": {"emoji": "🌧️", "emoji_unicode": "\U0001f327"}
            },
            "Light sleet": {
                "day": {"emoji": "🌨️", "emoji_unicode": "\U0001f328"},
                "night": {"emoji": "🌨️", "emoji_unicode": "\U0001f328"}
            },
            "Moderate or heavy sleet": {
                "day": {"emoji": "🌨️", "emoji_unicode": "\U0001f328"},
                "night": {"emoji": "🌨️", "emoji_unicode": "\U0001f328"}
            },
            "Patchy light snow": {
                "day": {"emoji": "🌨️", "emoji_unicode": "\U0001f328"},
                "night": {"emoji": "🌨️", "emoji_unicode": "\U0001f328"}
            },
            "Light snow": {
                "day": {"emoji": "🌨️", "emoji_unicode": "\U0001f328"},
                "night": {"emoji": "🌨️", "emoji_unicode": "\U0001f328"}
            },
            "Patchy moderate snow": {
                "day": {"emoji": "🌨️", "emoji_unicode": "\U0001f328"},
                "night": {"emoji": "🌨️", "emoji_unicode": "\U0001f328"}
            },
            "Moderate snow": {
                "day": {"emoji": "🌨️", "emoji_unicode": "\U0001f328"},
                "night": {"emoji": "🌨️", "emoji_unicode": "\U0001f328"}
            },    
            "Patchy heavy snow": {
                "day": {"emoji": "❄️", "emoji_unicode": "\u2744"},
                "night": {"emoji": "❄️", "emoji_unicode": "\u2744"}
            },
            "Heavy snow": {
                "day": {"emoji": "❄️", "emoji_unicode": "\u2744"},
                "night": {"emoji": "❄️", "emoji_unicode": "\u2744"}
            },
            "Ice pellets": {
                "day": {"emoji": "🧊", "emoji_unicode": "\U0001f9ca"},
                "night": {"emoji": "🧊", "emoji_unicode": "\U0001f9ca"}
            },
            "Light rain shower": {
                "day": {"emoji": "🌦️", "emoji_unicode": "\U0001f326"},
                "night": {"emoji": "🌧️", "emoji_unicode": "\U0001f327"}
            },
            "Moderate or heavy rain shower": {
                "day": {"emoji": "🌧️", "emoji_unicode": "\U0001f327"},
                "night": {"emoji": "🌧️", "emoji_unicode": "\U0001f327"}
            },
            "Torrential rain shower": {
                "day": {"emoji": "🌧️", "emoji_unicode": "\U0001f327"},
                "night": {"emoji": "🌧️", "emoji_unicode": "\U0001f327"}
            },
            "Light sleet showers": {
                "day": {"emoji": "🌨️", "emoji_unicode": "\U0001f328"},
                "night": {"emoji": "🌨️", "emoji_unicode": "\U0001f328"}
            },
            "Moderate or heavy sleet showers": {
                "day": {"emoji": "🌨️", "emoji_unicode": "\U0001f328"},
                "night": {"emoji": "🌨️", "emoji_unicode": "\U0001f328"}
            },
            "Light snow showers": {
                "day": {"emoji": "🌨️", "emoji_unicode": "\U0001f328"},
                "night": {"emoji": "🌨️", "emoji_unicode": "\U0001f328"}
            },
            "Moderate or heavy snow showers": {
                "day": {"emoji": "🌨️", "emoji_unicode": "\U0001f328"},
                "night": {"emoji": "🌨️", "emoji_unicode": "\U0001f328"}
            },
            "Light showers of ice pellets": {
                "day": {"emoji": "🧊", "emoji_unicode": "\U0001f9ca"},
                "night": {"emoji": "🧊", "emoji_unicode": "\U0001f9ca"}
            },
            "Moderate or heavy showers of ice pellets": {
                "day": {"emoji": "🧊", "emoji_unicode": "\U0001f9ca"},
                "night": {"emoji": "🧊", "emoji_unicode": "\U0001f9ca"}
            },
            "Patchy light rain in area with thunder": {
                "day": {"emoji": "⛈️", "emoji_unicode": "\u26c8"},
                "night": {"emoji": "⛈️", "emoji_unicode": "\u26c8"}
            },
            "Moderate or heavy rain in area with thunder": {
                "day": {"emoji": "⛈️", "emoji_unicode": "\u26c8"},
                "night": {"emoji": "⛈️", "emoji_unicode": "\u26c8"}
            },
            "Patchy light snow in area with thunder": {
                "day": {"emoji": "⛈️", "emoji_unicode": "\u26c8"},
                "night": {"emoji": "⛈️", "emoji_unicode": "\u26c8"}
            },
            "Moderate or heavy snow in area with thunder": {
                "day": {"emoji": "⛈️", "emoji_unicode": "\u26c8"},
                "night": {"emoji": "⛈️", "emoji_unicode": "\u26c8"}
            }
        }
    
        return emojis_dict
    
    
    
    @classmethod
    def print_emojis_dict(cls):
        """
        Print the emojis dictionary as a list of weather condition,
        time of the day and the corresponding emoji.
        """
        emojis_dict = cls.get_emojis_dict()
    
        for weather_key, weather_value in emojis_dict.items():
            for time_key, time_value in weather_value.items():
                print(time_value["emoji_unicode"], weather_key, "(", time_key, ")")
    
    
    @classmethod
    def write_json(cls, filename='weather_emojis.json'):
        """
        Store weather emojis dictionary into a JSON file
        """
        
        emojis_dict = cls.get_emojis_dict()
        
        # ensure_ascii=False to write Unicode characters directly, preserving emojis as literal characters
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(emojis_dict, f, ensure_ascii=False)
    
    
    
    @staticmethod
    def read_json(filename='weather_emojis.json'):
        """
        Read JSON file with weather emojis
        """
        
        with open(filename, 'r') as f:
            emojis_dict = json.load(f)
    
        return emojis_dict
    
    

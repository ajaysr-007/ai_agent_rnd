import urllib.request
import urllib.parse
import json

def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    try:
        city_encoded = urllib.parse.quote(city)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_encoded}&count=1"
        
        with urllib.request.urlopen(geo_url) as response:
            geo_data = json.loads(response.read().decode())
            
        if not geo_data.get("results"):
            return f"Error: Could not find location '{city}'."
            
        loc = geo_data["results"][0]
        lat, lon = loc["latitude"], loc["longitude"]
        full_name = f"{loc.get('name')}, {loc.get('country')}"
        
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        with urllib.request.urlopen(weather_url) as response:
            weather_data = json.loads(response.read().decode())
            
        current = weather_data.get("current_weather", {})
        temp = current.get("temperature")
        wind = current.get("windspeed")
        
        return f"The current weather in {full_name} is {temp}°C with wind speeds of {wind} km/h."
        
    except Exception as e:
        return f"Error fetching weather for {city}: {str(e)}"

WEATHER_FUNCTIONS = {
    "get_weather": get_weather
}

WEATHER_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a given city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city, e.g. 'San Francisco', 'London'"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

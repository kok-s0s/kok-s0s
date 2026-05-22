import re
import sys
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from urllib.error import URLError
import json

CITY = "Beijing"

CONDITION_EMOJI = {
    "sunny": "☀️", "clear": "☀️",
    "partly cloudy": "⛅", "partly": "⛅",
    "overcast": "☁️", "cloudy": "☁️",
    "rain": "🌧️", "drizzle": "🌦️", "shower": "🌦️",
    "snow": "❄️", "sleet": "🌨️", "blizzard": "🌨️",
    "thunder": "⛈️", "storm": "⛈️",
    "fog": "🌫️", "mist": "🌫️", "haze": "🌫️",
    "wind": "🌬️", "blowing": "🌬️",
}

def condition_to_emoji(desc: str) -> str:
    desc_lower = desc.lower()
    for keyword, emoji in CONDITION_EMOJI.items():
        if keyword in desc_lower:
            return emoji
    return "🌤️"

def fetch_weather(city: str) -> dict:
    url = f"https://wttr.in/{city}?format=j1"
    req = Request(url, headers={"User-Agent": "GitHub-README-Weather/1.0"})
    with urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())

def build_weather_section(city: str) -> str:
    data = fetch_weather(city)
    cur = data["current_condition"][0]

    desc = cur["weatherDesc"][0]["value"]
    emoji = condition_to_emoji(desc)
    temp_c = cur["temp_C"]
    feels_c = cur["FeelsLikeC"]
    humidity = cur["humidity"]
    wind_kmph = cur["windspeedKmph"]
    wind_dir = cur["winddir16Point"]

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return (
        f"| {emoji} | **{desc}** | 🌡️ `{temp_c}°C` &nbsp;*(feels {feels_c}°C)* |\n"
        f"|:---:|:---|:---|\n"
        f"| 💧 Humidity | `{humidity}%` | 📍 {city}, China |\n"
        f"| 💨 Wind | `{wind_kmph} km/h {wind_dir}` | 🕐 `{now}` |\n"
        f"\n"
        f"*Auto-updated every 3 hours via GitHub Actions*"
    )

def update_readme(section: str, path: str = "README.md") -> None:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = re.sub(
        r"<!-- WEATHER-START -->.*?<!-- WEATHER-END -->",
        f"<!-- WEATHER-START -->\n{section}\n<!-- WEATHER-END -->",
        content,
        flags=re.DOTALL,
    )

    if new_content == content:
        print("Warning: WEATHER markers not found in README.")
        sys.exit(1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

if __name__ == "__main__":
    try:
        section = build_weather_section(CITY)
        update_readme(section)
        print(f"✅ Weather updated for {CITY}")
        print(section)
    except URLError as e:
        print(f"❌ Network error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

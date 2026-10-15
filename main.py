import os
import telebot
from dotenv import load_dotenv
import requests
import time
import sqlite3

load_dotenv()

token = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(token)
weather_api = os.getenv("OPEN_WEATHER_API")

last_coordinates = {}
last_cities = {}

connection = sqlite3.connect("bot_databases.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS History (
id INTEGER PRIMARY KEY,
user_id INTEGER NOT NULL,
city TEXT NOT NULL,
searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

connection.commit()
cursor.close()
connection.close()

connection = sqlite3.connect("bot_databases.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Favorites(
user_id INTEGER NOT NULL,
favorite_city TEXT NOT NULL,
PRIMARY KEY (user_id, favorite_city)
)
""")


@bot.message_handler(commands=["help"])
def help(message):
    bot.reply_to(
        message,
        f"""
Weather Lentyay Bot - help:

Available Commands:
    * /start - Start using the bot.
    * /help - Show this help message.
    * /forecast - Get the weather forecast for the next 5 days.
    * /about - learn more about the bot.
    * /history - View your recent city search history.
    * /favorite - Access your favorite city.

How to use the bot
1. Send /start
2. Enter a city or village name, for example, Kyiv.
3. Check the current weather in the bot's reply.
4. Send /forecast to see the forecast.
""",
    )


@bot.message_handler(commands=["about"])
def about(message):
    bot.reply_to(
        message,
        f"""
Weather Lentyay Bot - about:

The bot was developed by @LentyayT9. This bot can give you a forecast for some days by the name of your city. 

Used technologies:
OpenWeatherMap(API) - https://openweathermap.org
pyTelegramBotAPI
Brains🧠

My GitHub🐱 - https://github.com/divan-netizen1 
""",
    )


@bot.message_handler(commands=["favorite"])
def favorite(message):
    user_id = message.from_user.id
    question = bot.reply_to(message, "Enter the your favorite city: ")
    bot.register_next_step_handler(question, share_favorite, user_id)


def share_favorite(message, user_id):
    city = message.text.strip()

    if not city:
        bot.reply_to(message, "City cannot be empty")

    connection = sqlite3.connect("bot_databases.db")
    cursor = connection.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO Favorites (user_id, favorite_city) VALUES (?, ?)",
        (user_id, city),
    )
    connection.commit()
    cursor.close()
    connection.close()
    bot.reply_to(message, f"⭐ {city} saved to favorites!")


@bot.message_handler(commands=["start"])
def start(message):

    user = getattr(message, "from_user", None)
    user_first_name = (
        user.first_name if user and getattr(user, "first_name", None) else "friend"
    )
    bot.reply_to(
        message, f"Hello! {user_first_name}, enter the name of your city or village:"
    )


@bot.message_handler(commands=["history"])
def history(message):
    user_id = message.from_user.id
    connection = sqlite3.connect("bot_databases.db")
    cursor = connection.cursor()

    cursor.execute(
        """
SELECT city, searched_at 
FROM History
WHERE user_id = ?
ORDER BY id DESC
LIMIT 10""",
        (user_id,),
    )
    cities = cursor.fetchall()
    cursor.close()
    connection.close()

    if not cities:
        bot.reply_to(message, "Your search history is empty.")
        return
    print(f"Some five from DB - {cities}")

    history_message = f"🕐 Your last 5 city searches: \n\n"

    for city, searched_at in cities:
        history_message += f"📍 {city} — {searched_at}\n\n"

    bot.reply_to(message, history_message)


def fetch_weather(lat, lon):

    response = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather",
        params={
            "lat": lat,
            "lon": lon,
            "appid": weather_api,
            "units": "metric",
            "lang": "uk",
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()  # get { 'coord': {lon: 12.345, lat:12.345}


@bot.message_handler(commands=["forecast"])
def forecast(message):
    coordinates = last_coordinates.get(message.chat.id)
    if not coordinates:
        bot.reply_to(message, "Please enter a city or village name first.")
        return
    lat, lon = coordinates
    try:
        forecast_response = requests.get(
            f"https://api.openweathermap.org/data/2.5/forecast",
            params={
                "lat": lat,
                "lon": lon,
                "appid": weather_api,
                "units": "metric",
                "lang": "uk",
            },
            timeout=10,
        )
        forecast_response.raise_for_status()
    except requests.exceptions.HTTPError:
        bot.reply_to(message, "Error: Unable to fetch data from the weather service.")
        print("HTTP error !")
        return
    except requests.exceptions.ConnectionError:
        bot.reply_to(
            message, "Error: Connection error. Please check your internet connection."
        )
        print("Connection error !")
        return
    except requests.exceptions.Timeout:
        bot.reply_to(message, "Error: Request timed out. Please try again later.")
        print("Timeout error !")
        return
    except requests.exceptions.RequestException as exc:
        bot.reply_to(message, "Error: Unable to fetch data from the weather service.")
        print(f"Request error: {exc}")
        return

    forecast_data = forecast_response.json()

    forecast_info = forecast_data.get("list", [])

    city_name = last_cities.get(message.chat.id, "Unknown place!")

    forecast_by_day = {}

    is_first = True

    for days_data in forecast_info:
        dt_txt = days_data.get("dt_txt", "Unknown time")
        sliced_data = dt_txt[:10]

        if not sliced_data in forecast_by_day:
            forecast_by_day[sliced_data] = []

        forecast_by_day[sliced_data].append(days_data)

    for key in forecast_by_day:
        container = []

        for data in forecast_by_day[key]:
            temperature = data.get("main", {}).get("temp", "Unknown temperature")
            if isinstance(temperature, (int, float)):
                container.append(temperature)
            else:
                print("Temperature isn't a number!")
                return

        average = sum(container) / len(container) if container else 0
        day_message = f"""

📆 Forecast for {key}| Average daily temperature: {average:.1f}°C 

🌍Place: {city_name} :\n\n """

        for data in forecast_by_day[key]:
            dt_txt = data.get("dt_txt", "Unknown time")
            feels_like = data.get("main", {}).get("feels_like", "Undefined")
            temperature = data.get("main", {}).get("temp", "Unknown temperature")
            weather_type = data.get("weather", [{}])[0].get("main", "Undefined")
            description = data.get("weather", [{}])[0].get("description", "Undefined")
            wind = data.get("wind", {}).get("speed", "Undefined")
            humidity = data.get("main", {}).get("humidity", "Undefined")
            daily_time = dt_txt[11:16]
            head_forecast = f""" 
---------------------------------------------------------------------
⏰Time: {daily_time} 

🌡 Temperature: {temperature}°C | (✋ Feels like: {feels_like})°C

🌤 Weather: {weather_type} - ☁️ Description: {description}

💨 Wind speed: {wind} m/s | 💧 Humidity: {humidity}%
 """
            day_message += head_forecast
        if not is_first:
            time.sleep(0.8)
        bot.send_message(message.chat.id, day_message)
        is_first = False


@bot.message_handler(content_types=["text"])
def get_weather(message):
    id_person = message.from_user.id
    city = message.text.strip().lower()
    try:
        place_response = requests.get(
            f"https://api.openweathermap.org/geo/1.0/direct?q={city}&appid={weather_api}",
            timeout=10,
        )
        place_response.raise_for_status()
    except requests.exceptions.HTTPError:
        bot.reply_to(message, "Error: Unable to fetch data from the weather service.")
        print("HTTP error !")
        return
    except requests.exceptions.ConnectionError:
        bot.reply_to(
            message, "Error: Connection error. Please check your internet connection."
        )
        print("Connection error !")
        return
    except requests.exceptions.Timeout:
        bot.reply_to(message, "Error: Request timed out. Please try again later.")
        print("Timeout error !")
        return
    except requests.exceptions.RequestException as exc:
        bot.reply_to(message, "Error: Unable to fetch data from the weather service.")
        print(f"Request error: {exc}")
        return

    print(city)
    print(f"ID person is - {id_person}")

    geo = place_response.json()
    if not geo:
        bot.reply_to(message, f"Undefined place: {city}")
        return

    city_info = geo[0]
    city_history = city_info.get("name", city)
    local_names = city_info.get("local_names", {})
    eng_name = local_names.get("en", city_info.get("name", city))
    ukr_name = local_names.get("uk", city_info.get("name", city))
    country = city_info.get("country", "Unknown")
    region = city_info.get("state", "Undefined")
    last_cities[message.chat.id] = city_history

    connection = sqlite3.connect("bot_databases.db")
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO History (user_id, city) VALUES (?, ?)", (id_person, city_history)
    )
    connection.commit()
    cursor.execute(
        "SELECT city FROM History WHERE user_id = ? ORDER BY id DESC LIMIT 5",
        (id_person,),
    )
    some_five = cursor.fetchall()
    print(f"The last cities from DB - {some_five}\n")
    connection.commit()
    cursor.close()
    connection.close()

    bot.send_message(
        message.chat.id,
        f"Назва українською - 🇺🇦 : {ukr_name}\n"
        f"Name in English - 🇺🇸 : {eng_name}\n"
        f"-----------------------------\n"
        f"Country (code): {country}\n"
        f"State/region: {region}",
    )
    lat = city_info["lat"]
    lon = city_info["lon"]
    last_coordinates[message.chat.id] = (lat, lon)
    print("lat", lat)
    print("lon", lon)

    try:
        weather = fetch_weather(lat, lon)
    except requests.exceptions.RequestException as exc:
        bot.reply_to(message, "Error: Unable to fetch data from the weather service.")
        print(f"Weather request error: {exc}")
        return

    weather_type = weather["weather"][0]["main"]
    description = weather["weather"][0]["description"]
    temperature = weather["main"]["temp"]
    feels = weather["main"]["feels_like"]
    wind = weather["wind"]["speed"]

    bot.reply_to(
        message,
        f"""🌡 Temperature now: {temperature} °C
-------------------------
🖐 Feels like: {feels} °C
-------------------------
💨 Wind speed: {wind} m/s
-------------------------
🌧 Weather: {weather_type}
-------------------------
☁️ Description: {description}""",
    )
    bot.send_message(
        message.chat.id,
        "Do you want to see the forecast for the next 5 days? Type /forecast",
    )
    print(temperature, "temperature °C")


print("Bot started!")
bot.infinity_polling()

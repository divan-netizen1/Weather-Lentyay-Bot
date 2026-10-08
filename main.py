import os
import telebot
from dotenv import load_dotenv
import requests
import json

load_dotenv()

token = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(token)
weather_api = os.getenv("OPEN_WEATHER_API")


@bot.message_handler(commands=["start"])
def start(message):
    user = getattr(message, "from_user", None)
    user_first_name = (
        user.first_name if user and getattr(user, "first_name", None) else "friend"
    )
    bot.reply_to(
        message, f"Hello! {user_first_name}, enter the name of your city or village:"
    )


@bot.message_handler(content_types=["text"])
def get_weather(message):
    city = message.text.strip().lower()
    try:
        place_response = requests.get(
            f"http://api.openweathermap.org/geo/1.0/direct?q={city}&appid={weather_api}",
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

    normal_name = city.capitalize()
    print("User enter:", normal_name)
    print(city)

    geo = place_response.json()
    if not geo:
        bot.reply_to(message, f"Undefined place: {city}")
        return

    city_info = geo[0]
    local_names = city_info.get("local_names", {})
    eng_name = local_names.get("en", city_info.get("name", city))
    ukr_name = local_names.get("uk", city_info.get("name", city))
    country = city_info.get("country", "Unknown")
    region = city_info.get("state", "Undefined")
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
    print("lat", lat)
    print("lon", lon)
    try:
        weather_response = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather_api}&units=metric&lang=uk",
            timeout=10,
        )
        weather_response.raise_for_status()
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

    weather = weather_response.json()

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
    print(temperature, "°C")


print("Bot started!")
bot.infinity_polling()

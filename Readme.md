# 🌦️ Weather Lentyay Bot

A Telegram bot built with Python that provides current weather information and a five-day weather forecast for a city or village.

The project uses the OpenWeatherMap API to retrieve weather data and SQLite to store users' search history and favorite cities.

## ✨ Features

- 🌡️ **Current weather** — get the current temperature, feels-like temperature, wind speed, and weather description.
- 📅 **Five-day forecast** — view forecast data grouped by day, including temperatures, humidity, wind speed, and weather conditions.
- 🌍 **Geocoding** — find a location by its name and retrieve its geographical coordinates.
- 🗺️ **Location information** — display the location name in Ukrainian and English, as well as its country and region when available.
- 🕐 **Search history** — view your ten most recent city searches.
- ⭐ **Favorite cities** — save a city to your favorites.
- 🆘 **Help command** — view instructions on how to use the bot.
- ℹ️ **About command** — learn more about the project and its technologies.
- 🛡️ **Error handling** — handle common HTTP, connection, and timeout errors when communicating with the weather API.

## 🛠️ Technologies

- **Python** — the main programming language.
- **pyTelegramBotAPI** — interaction with the Telegram Bot API.
- **Requests** — sending HTTP requests to external APIs.
- **SQLite** — storing search history and favorite cities.
- **python-dotenv** — loading environment variables from a `.env` file.
- **OpenWeatherMap API** — retrieving geographical and weather data.

## 📱 Bot Commands

| Command | Description |
|---|---|
| `/start` | Start using the bot and enter a city or village name. |
| `/help` | Display usage instructions. |
| `/about` | Display information about the project. |
| `/forecast` | Get the five-day weather forecast for the last searched location. |
| `/history` | View the ten most recent city searches. |
| `/favorite` | Save a city to your favorites. |

## 🚀 Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/divan-netizen1/Weather-Lentyay-Bot.git
cd Weather-Lentyay-Bot
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate the environment.

**Windows:**

```bash
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install pyTelegramBotAPI requests python-dotenv
```

### 4. Configure environment variables

Create a `.env` file in the root directory of the project:

```env
BOT_TOKEN=your_telegram_bot_token
OPEN_WEATHER_API=your_openweathermap_api_key
```

Replace the placeholder values with your own credentials.

- `BOT_TOKEN` — the token obtained from [@BotFather](https://t.me/BotFather).
- `OPEN_WEATHER_API` — your API key from [OpenWeatherMap](https://openweathermap.org/api).

**Important:** Never commit your `.env` file or expose your API keys in a public repository.

### 5. Run the bot

```bash
python main.py
```

Open your bot in Telegram and send `/start`.

## 🗂️ Project Structure

```text
Weather-Lentyay-Bot/
├── main.py
├── .gitignore
├── README.md
└── .env                 # Local configuration; not committed
```

The `bot_databases.db` SQLite database is created automatically when the application runs. It stores search history and favorite cities.

## 🌦️ How It Works

1. The user sends a city or village name to the bot.
2. The bot sends a request to the OpenWeatherMap Geocoding API.
3. The API returns location information and geographical coordinates.
4. The bot requests current weather data using those coordinates.
5. The bot displays the weather information in Telegram.
6. The location is saved in the user's search history.
7. The user can request a five-day forecast or use other bot commands.

## 🔮 Future Improvements

- Improve the favorite-city feature so users can select and retrieve saved cities.
- Add more comprehensive error handling and input validation.
- Improve database management and separate database operations from bot handlers.
- Add automated tests.
- Refactor the application into separate modules as the project grows.

## 👨‍💻 Author

**Developer:** [@LentyayT9](https://github.com/divan-netizen1)

**Repository:** [Weather-Lentyay-Bot](https://github.com/divan-netizen1/Weather-Lentyay-Bot)

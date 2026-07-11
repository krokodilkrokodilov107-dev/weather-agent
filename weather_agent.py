import anthropic
import json
import os
import requests


cities_history = []

WEATHER_CODES = {
    "01d": "☀️ Ясно",
    "01n": "🌙 Ясно (ночь)",
    "02d": "⛅ Немного облаков",
    "02n": "🌤️ Немного облаков (ночь)",
    "03d": "☁️ Облачно",
    "03n": "☁️ Облачно (ночь)",
    "04d": "☁️ Пасмурно",
    "04n": "☁️ Пасмурно (ночь)",
    "09d": "🌧️ Морось",
    "09n": "🌧️ Морось (ночь)",
    "10d": "🌦️ Дождь",
    "10n": "🌧️ Дождь (ночь)",
    "11d": "⛈️ Гроза",
    "11n": "⛈️ Гроза (ночь)",
    "13d": "❄️ Снег",
    "13n": "❄️ Снег (ночь)",
    "50d": "🌫️ Туман",
    "50n": "🌫️ Туман (ночь)",
}

WEATHER_TRANSLATIONS = {
    "clear sky": "ясно",
    "few clouds": "немного облаков",
    "scattered clouds": "облачно",
    "broken clouds": "пасмурно",
    "shower rain": "ливень",
    "rain": "дождь",
    "thunderstorm": "гроза",
    "snow": "снег",
    "mist": "туман",
    "light rain": "лёгкий дождь",
    "moderate rain": "умеренный дождь",
    "heavy rain": "сильный дождь",
    "light snow": "лёгкий снег",
    "heavy snow": "сильный снег",
    "sleet": "мокрый снег",
    "drizzle": "морось",
    "light intensity drizzle": "лёгкая морось",
    "heavy intensity drizzle": "интенсивная морось",
    "light intensity shower rain": "лёгкий ливень",
    "heavy intensity shower rain": "сильный ливень",
    "ragged shower rain": "прерывистый ливень",
    "thunderstorm with light rain": "гроза с лёгким дождём",
    "thunderstorm with rain": "гроза с дождём",
    "thunderstorm with heavy rain": "гроза с сильным дождём",
    "light thunderstorm": "слабая гроза",
    "heavy thunderstorm": "сильная гроза",
    "ragged thunderstorm": "прерывистая гроза",
    "light snow shower": "лёгкий снегопад",
    "heavy snow shower": "сильный снегопад",
}


def get_weather(city: str, fail: bool = False) -> dict:
    """Получает данные о погоде в городе от OpenWeatherMap API"""
    if fail:
        raise Exception(f"Ошибка при получении данных о погоде для города '{city}'")

    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise Exception("Не установлена переменная окружения OPENWEATHER_API_KEY")

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "en"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    weather_code = data["weather"][0]["icon"]
    description_ru = WEATHER_CODES.get(weather_code)

    if not description_ru:
        description_en = data["weather"][0]["description"].lower()
        description_ru = WEATHER_TRANSLATIONS.get(description_en, description_en)

    return {
        "temperature": int(data["main"]["temp"]),
        "description": description_ru
    }


def return_history() -> list:
    """Возвращает список городов, к которым обращался пользователь в текущей сессии"""
    return cities_history


def get_temperature_advice(temperature: int) -> str:
    """Возвращает совет что надеть при такой температуре"""
    if temperature < -15:
        return "Одевайтесь очень тепло! Нужна тёплая зимняя куртка, шапка, шарф, варежки и тёплые ботинки. Избегайте длительного пребывания на улице."
    elif temperature < -5:
        return "Холодно! Надевайте зимнюю куртку, шапку, шарф и тёплые ботинки. Не забудьте варежки."
    elif temperature < 0:
        return "Мороз. Рекомендуется зимняя куртка, шапка, шарф и тёплая обувь."
    elif temperature < 10:
        return "Прохладно. Надевайте демисезонную куртку, свитер и вторые носки. Шапка и перчатки желательны."
    elif temperature < 15:
        return "Прохладная погода. Кофта или лёгкая куртка будут кстати."
    elif temperature < 20:
        return "Комфортная температура. Рубашка или тонкий свитер — достаточно."
    elif temperature < 25:
        return "Тепло. Можно надеть лёгкую рубашку или футболку. Возьмите лёгкую кофту на случай ветра."
    else:
        return "Жарко! Надевайте лёгкую одежду: футболку, шорты, лёгкие брюки. Не забудьте солнечные очки и защиту от солнца."


def compare_weather(cities: list) -> dict:
    """Сравнивает погоду в нескольких городах и возвращает анализ"""
    if not cities or len(cities) < 2:
        raise Exception("Для сравнения необходимо указать минимум 2 города")

    weather_data = {}
    try:
        for city in cities:
            if city not in cities_history:
                cities_history.append(city)
            weather_data[city] = get_weather(city)
    except Exception as e:
        raise Exception(f"Ошибка при получении данных о погоде: {str(e)}")

    temperatures = [data["temperature"] for data in weather_data.values()]
    warmest_city = max(weather_data.keys(), key=lambda c: weather_data[c]["temperature"])
    coldest_city = min(weather_data.keys(), key=lambda c: weather_data[c]["temperature"])
    temp_diff = weather_data[warmest_city]["temperature"] - weather_data[coldest_city]["temperature"]

    comparison = {
        "cities": weather_data,
        "warmest": {"city": warmest_city, "temperature": weather_data[warmest_city]["temperature"]},
        "coldest": {"city": coldest_city, "temperature": weather_data[coldest_city]["temperature"]},
        "temperature_difference": temp_diff,
        "average_temperature": int(sum(temperatures) / len(temperatures))
    }

    return comparison


def i_need_help() -> str:
    """Возвращает справку о доступных инструментах"""
    help_text = """📚 Доступные инструменты:

1. get_weather — Указать город
2. get_temperature_advice — Указать градусы
3. return_history — Без параметров
4. compare_weather — Список городов
5. i_need_help — Без параметров

Обращайтесь вежливо, и я с удовольствием помогу! 😊"""
    return help_text


def process_tool_call(tool_name: str, tool_input: dict) -> str:
    """Обрабатывает вызовы инструментов"""
    if tool_name == "get_weather":
        try:
            city = tool_input["city"]
            if city not in cities_history:
                cities_history.append(city)
            result = get_weather(city)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            error_message = f"Ошибка при получении информации о погоде: {str(e)}"
            return json.dumps({"error": error_message}, ensure_ascii=False)
    elif tool_name == "get_temperature_advice":
        try:
            result = get_temperature_advice(tool_input["temperature"])
            return result
        except Exception as e:
            return f"Ошибка при получении совета по одежде: {str(e)}"
    elif tool_name == "return_history":
        try:
            result = return_history()
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)
    elif tool_name == "compare_weather":
        try:
            cities = tool_input["cities"]
            result = compare_weather(cities)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            error_message = f"Ошибка при сравнении погоды: {str(e)}"
            return json.dumps({"error": error_message}, ensure_ascii=False)
    elif tool_name == "i_need_help":
        try:
            result = i_need_help()
            return result
        except Exception as e:
            return f"Ошибка при получении справки: {str(e)}"
    else:
        return f"Неизвестный инструмент: {tool_name}"


def weather_agent(user_question: str) -> str:
    """Основной агент для ответов о погоде"""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    tools = [
        {
            "name": "get_weather",
            "description": "Получить информацию о погоде в указанном городе. Возвращает текущую температуру и описание погодных условий.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Название города, для которого нужно получить информацию о погоде",
                    }
                },
                "required": ["city"],
            },
        },
        {
            "name": "get_temperature_advice",
            "description": "Получить совет о том, что надеть при определённой температуре",
            "input_schema": {
                "type": "object",
                "properties": {
                    "temperature": {
                        "type": "integer",
                        "description": "Температура в градусах Цельсия",
                    }
                },
                "required": ["temperature"],
            },
        },
        {
            "name": "return_history",
            "description": "Получить список всех городов, к которым пользователь обращался в текущей сессии",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        {
            "name": "compare_weather",
            "description": "Сравнить погоду в двух и более городах. Возвращает температуру в каждом городе, самый тёплый и холодный город, разницу температур и среднюю температуру.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "cities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Список названий городов для сравнения (минимум 2 города)",
                    }
                },
                "required": ["cities"],
            },
        },
        {
            "name": "i_need_help",
            "description": "Получить справку о всех доступных инструментах и способах их использования",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    ]

    messages = [{"role": "user", "content": user_question}]

    system_prompt = "Ты — помощник по погоде. Отвечай на все вопросы пользователя на русском языке. Используй доступные инструменты для получения информации о погоде и советов по одежде. Будь вежлив и полезен."

    while True:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system_prompt,
            tools=tools,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return "Извините, не удалось получить ответ."

        if response.stop_reason == "tool_use":
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_use_id = block.id

                    result = process_tool_call(tool_name, tool_input)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": result,
                        }
                    )

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    return "Извините, не удалось получить ответ."


if __name__ == "__main__":
    print("🌤️ Добро пожаловать в погодного помощника!")
    print("Введите свой вопрос о погоде или совет по одежде.")
    print("Для выхода введите 'exit'\n")

    while True:
        try:
            user_input = input("❓ Ваш вопрос: ").strip()

            if user_input.lower() in ["exit", "выход", "quit"]:
                print("\n👋 До свидания!")
                break

            if not user_input:
                print("⚠️ Пожалуйста, введите вопрос.\n")
                continue

            print("-" * 50)
            answer = weather_agent(user_input)
            print(f"✅ Ответ: {answer}")
            print()
        except KeyboardInterrupt:
            print("\n\n👋 До свидания!")
            break

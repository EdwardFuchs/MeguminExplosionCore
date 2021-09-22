# Модуль погоды для ядра BAB
# Версия: 2.5
# Авторы: https://vk.com/edwardfuchs


# Предустановка библиотек
from core.requirements import check_and_install

requirements = ["Pillow"]
check_and_install(requirements)

# Импортирование нужных библиотек
from PIL import Image, ImageFont, ImageDraw  # Для создания и редактирования изображений
import requests  # Для запросов на сайт
import datetime  # Для получения времени
from io import BytesIO  # Для сохранения файла в оперативную память
import os.path  # Для проверки существования файла
from random import choice

# Настройка:
appId = "****************************************"  # APPID https://openweathermap.org/appid#signup
use_graphic = True  # Использовать ли графику
font_name = "NotoSans-Regular.ttf"
font_url = "https://github.com/EdwardFuchs/furry-sniffle/blob/main/NotoSans-Regular.ttf?raw=true"


# Функция для получения погоды
def get_weather(city):
    weather = requests.get('http://api.openweathermap.org/data/2.5/weather', params={
        "lang": "ru",
        "units": "metric",
        "APPID": appId,
        "q": city
    }).json()
    if int(weather["cod"]) == 404:
        raise ValueError(f"404: Город {city} не найден.")
    elif int(weather["cod"]) != 200:
        raise Exception(f"{weather['message']}")
    icon = weather["weather"][0]["icon"]
    temp = weather["main"]["temp"]
    temp_min = weather["main"]["temp_min"]
    temp_max = weather["main"]["temp_max"]
    utc = weather["timezone"]
    country = weather['sys']['country']
    weather_desc = weather["weather"][0]["description"]
    wind_speed = weather["wind"]["speed"]
    clouds = weather["clouds"]["all"]
    humidity = weather["main"]["humidity"]
    time_update = datetime.datetime.fromtimestamp(weather["dt"]).strftime("%H:%M")
    return city, country, icon, temp, temp_min, temp_max, utc, weather_desc, wind_speed, clouds, humidity, time_update


def with_graphic(bot, city, country, icon, temp, temp_min, temp_max, utc):
    # Иконка
    icon_url = f"http://openweathermap.org/img/wn/{icon}@4x.png"
    icon = Image.open(requests.get(icon_url, stream=True).raw)
    icon = icon.resize([300, 300], resample=Image.LANCZOS)
    # Проверка наличия шрифта
    font_path = f"Files/Fonts/{font_name}"
    if not os.path.isfile(font_path):
        bot.send("Похоже вы в певый раз запустили графический плагин. Скачиваем нужный шрифт и помещаем его в нужное место...")
        if not os.path.exists("Files") or not os.path.exists("Files/Fonts"):
            bot.send("Создаем папку Files/Fonts/")
            os.makedirs("Files/Fonts/")
        fnt = requests.get(f"{font_url}")
        with open(font_path, "wb") as f:
            f.write(fnt.content)
        bot.send("Шрифт скачан и помещен в нужное место.")
    # Задаем шрифт
    small = ImageFont.truetype(font_path, 48)
    big = ImageFont.truetype(font_path, 128)
    # Создаем изображение
    img = Image.new("RGB", (1080, 400), "#000000")
    draw = ImageDraw.Draw(img)
    # Текст по центру
    w, h = draw.textsize(f"{country}/{city}", font=small)
    draw.text((((1080 - w) / 2), 20), f"{country}/{city}", font=small, fill=(255, 255, 255))
    # Часы
    offset = datetime.timedelta(seconds=utc)  # отступ по UTC
    tz = datetime.timezone(offset, name=city)
    dt = datetime.datetime.now(tz=tz)
    time = dt.strftime("%H:%M")
    draw.text((205, 70), time, font=big, fill=(255, 255, 255))
    draw.text((530, 60), "|", font=big, fill=(255, 255, 255))
    data = dt.strftime("%A, %d %B")
    # на русский
    data = data.replace("Monday", "Понедельник").replace("Tuesday", "Вторник").replace("Wednesday", "Среда").replace("Thursday", "Четверг").replace("Friday", "Пятница").replace("Saturday", "Суббота").replace("Sunday", "Воскресенье")
    data = data.replace("January", "Января").replace("February", "Февраля").replace("March", "Марта").replace("April", "Апреля").replace("May", "Мая").replace("June", "Июня").replace("July", "Июля").replace("August", "Августа").replace("September", "Сентября").replace("October", "Октября").replace("November", "Ноября").replace("December", "Декабря")
    # Текст по центру
    w, h = draw.textsize(data, font=small)
    draw.text((((1080 - w) / 2), 300), data, font=small, fill=(255, 255, 255))
    # ставим значёк погоды
    img.paste(icon, (520, 20), icon)
    # температуры
    draw.text((800, 100), f"{int(temp)}°", font=small, fill=(255, 255, 255))
    draw.text((800, 160), f"{int(temp_min)}°/{int(temp_max)}°", font=small, fill=(255, 255, 255))
    temp = BytesIO()
    img.save(temp, format="png")
    # event.bot.upload_files(files, event.peer_id)
    img.close()
    return temp


def without_graphic(city, country, temp, utc, weather_desc, wind_speed, clouds, humidity, time_update):
    current_weather = f"""Погода в {country}/{city}:
            &#8195;•Температура: {temp}°C
            &#8195;•Состояние: {weather_desc}
            &#8195;•Скорость ветра: {wind_speed} м/с
            &#8195;•Облачность: {clouds}%
            &#8195;•Влажность: {humidity}%
            &#8195;•Время обновления: {time_update} UTC{f"+{utc / 3600}" if utc >= 0 else utc / 3600}"""
    return current_weather


def vk_upload_photo(bot, file):
    token = choice(bot.tokens)
    res = bot.photos.getMessagesUploadServer(group_id=bot.group_id, peer_id=bot.from_id, access_token=token)
    ret = bot.post(res["response"]["upload_url"], files={"file1": ("weather.png", file.getvalue())})  # поддержка proxy
    ret = bot.photos.saveMessagesPhoto(v="5.87", server=ret["server"], photo=ret["photo"], hash=ret["hash"])["response"][0]
    return f'photo{ret["owner_id"]}_{ret["id"]}'


def weather(bot):
    if not bot.text:
        if bot.event == "message_new":
            try:
                city = bot.users.get(user_ids=bot.from_id, fields="city, country")["response"][0]["city"]["title"]
            except:
                bot.send("Ошибка! В команде нужно указывать город или открыть в информации профиля.")
                return
        else:
            bot.send("Ошибка! В команде нужно указывать город.")
            return
    else:
        city = bot.text
    city, country, icon, temp, temp_min, temp_max, utc, weather_desc, wind_speed, clouds, humidity, time_update = get_weather(city)
    if use_graphic:
            file = with_graphic(bot, city, country, icon, temp, temp_min, temp_max, utc)
            if bot.event == "message_new":
                try:
                    attachment = vk_upload_photo(bot, file)
                    bot.send("", attachment=attachment)
                except Exception as e:
                    print(e)
                    bot.send(f"[ERROR] [{bot._name}]: {e}", peer_id=bot.error_chat)
                    bot.send("", attachment="photo-169151978_457733782")
            else:
                bot.send(f"[{bot._name}]: Нет нужного эвента для загрузки фото")
            file.close()
    else:
        res = without_graphic(city, country, temp, utc, weather_desc, wind_speed, clouds, humidity, time_update)
        bot.send(res)


cmd = {weather: "погода"}

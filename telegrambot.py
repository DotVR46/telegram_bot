import telebot
from telebot import types
import requests
import config
import datetime

# https://api.openweathermap.org/data/2.5/onecall?lon=74.59&lat=42.87&exclude=hourly,minutely,current,alerts&appid=a9625fde9a815d299c2e9a3e73429e71

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start', 'старт'])
def welcome(message):
    bot.send_message(message.chat.id, 'Добро пожаловать!' + '\n'
                     + 'Напиши название города и я покажу тебе погоду!')


@bot.message_handler(content_types=['text'])
def weather_send(message):
    global city
    city = message.text
    global mess
    mess = message

    try:
        weather = get_json()
        keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
        key_current = types.InlineKeyboardButton(
            text='Сейчас', callback_data='current')
        keyboard.add(key_current)
        key_daily = types.InlineKeyboardButton(
            text='На неделю', callback_data='daily')
        keyboard.add(key_daily)
        question = 'На какой период показать погоду?'
        bot.send_message(message.from_user.id, text=question,
                         reply_markup=keyboard)

    except:
        bot.send_message(message.chat.id, 'Город ' + city + ' не найден!')


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    weather = get_json()
    if call.data == "current":  # call.data это callback_data, которую мы указали при объявлении кнопки
        try:

            bot.send_message(mess.chat.id, 'В городе '
                             + str(weather['name']) + ' температура: '
                             + str(float(weather['main']['temp'])) + ' °C' + '\n'
                             + 'Максимальная температура: '
                             + str(float(weather['main']
                                         ['temp_max'])) + ' °C' + '\n'
                             + 'Минимальная температура: '
                             + str(float(weather['main']
                                         ['temp_min'])) + ' °C' + '\n'
                             + 'Давление: '
                             + str(float(weather['main']['pressure'])) + '\n'
                             + 'Влажность: '
                             + str(float(weather['main']['humidity'])) + ' %' + '\n')
        except:
            bot.send_message(mess.chat.id, 'Город ' + city + ' не найден!')



    elif call.data == "daily":
        lon, lat = get_json()['coord']['lon'], get_json()['coord']['lat']
        url = f'https://api.openweathermap.org/data/2.5/onecall?lon={lon}&lat={lat}&exclude=hourly,minutely,current,alerts&appid={config.api_key}&units=metric'
        result = requests.get(url)
        weather = result.json()
        bot.send_message(mess.chat.id, 'Погода на сегодня и ближайшую неделю')
        count = 0
        while count < 8:
            bot.send_message(mess.chat.id, get_forecast(count, weather))
            count += 1


def get_json():
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={config.api_key}&units=metric'
    result = requests.get(url)
    weather = result.json()
    return weather


def get_date(timestamp):
    days=["Понедельник","Вторник","Среда","Четверг","Пятница","Суббота","Воскресенье"]
    weekday = datetime.datetime.fromtimestamp(timestamp).weekday()
    return str(datetime.datetime.fromtimestamp(timestamp)) + ' ' + days[weekday]


def get_forecast(count, weather):
    forecast = get_date(weather.get('daily')[count].get('dt')) + '\n' + 'Минимальная: ' + str(float(weather.get('daily')[count].get('temp').get('min'))) + ' °C' + '\n' + 'Максимальная: ' + str(float(weather.get('daily')[
        count].get('temp').get('max'))) + ' °C' + '\n' + 'Давление: ' + str(float(weather.get('daily')[count].get('pressure'))) + '\n' + 'Влажность: ' + str(float(weather.get('daily')[count].get('humidity'))) + ' %' + '\n'
    return forecast


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)

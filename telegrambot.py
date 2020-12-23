import telebot
from telebot import types
import requests
import datetime
from urllib.request import urlopen
import config



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
        if weather['name'] != None:
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
        else:
            bot.send_message(message.chat.id, 'Город ' + city + ' не найден!')
    except:
        bot.send_message(message.chat.id, 'Город ' + city + ' не найден!')


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    weather = get_json()
    if call.data == "current":  # call.data это callback_data, которую мы указали при объявлении кнопки
        try:
        	icon = weather.get('weather')[0].get('icon')
        	url = f'http://openweathermap.org/img/wn/{icon}@4x.png'

        	bot.send_photo(mess.chat.id, url, caption='В городе ' + str(weather['name'])\
        	+ ' температура: ' + str(float(weather['main']['temp'])) + ' °C' + '\n'\
        	+ 'Максимальная температура: ' + str(float(weather['main']['temp_max'])) + ' °C' + '\n'\
        	+ 'Минимальная температура: ' + str(float(weather['main']['temp_min'])) + ' °C' + '\n'\
        	+ 'Давление: ' + str(weather['main']['pressure']) + '\n'\
        	+ 'Влажность: ' + str(float(weather['main']['humidity'])) + ' %' + '\n')


        except:
            bot.send_message(mess.chat.id, 'Город ' + city + ' не найден!')



    elif call.data == "daily":
        lon, lat = get_json()['coord']['lon'], get_json()['coord']['lat']
        url = f'https://api.openweathermap.org/data/2.5/onecall?lon={lon}&lat={lat}\
        &exclude=hourly,minutely,current,alerts&appid={config.api_key}&units=metric'
        result = requests.get(url)
        weather = result.json()
        bot.send_message(mess.chat.id, 'Погода на сегодня и ближайшую неделю')
        count = 0
        while count < 8:
            bot.send_photo(mess.chat.id, get_icon(count, weather), caption=get_forecast(count, weather))
            count += 1


def get_json():
    url = f'http://api.openweathermap.org/data/2.5/weather?\
    q={city}&appid={config.api_key}&units=metric'
    result = requests.get(url)
    weather = result.json()
    return weather


def get_date(timestamp):
    days=["Понедельник","Вторник","Среда","Четверг","Пятница","Суббота","Воскресенье"]
    weekday = datetime.datetime.fromtimestamp(timestamp).weekday()
    return str(datetime.datetime.fromtimestamp(timestamp)) + ' ' + days[weekday]


def get_forecast(count, weather):
    forecast = get_date(weather.get('daily')[count].get('dt')) + '\n'\
    + 'Минимальная: ' + str(float(weather.get('daily')[count].get('temp').get('min'))) + ' °C' + '\n'\
    + 'Максимальная: ' + str(float(weather.get('daily')[count].get('temp').get('max'))) + ' °C' + '\n'\
    + 'Давление: ' + str(weather.get('daily')[count].get('pressure')) + '\n'\
    + 'Влажность: ' + str(float(weather.get('daily')[count].get('humidity'))) + ' %' + '\n'
    return forecast


def get_icon(count, weather):
	icon = weather.get('daily')[count].get('weather')[0].get('icon')
	url = f'http://openweathermap.org/img/wn/{icon}@4x.png'
	return url

if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)

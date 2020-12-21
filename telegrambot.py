import telebot
import requests
import config

# https://api.openweathermap.org/data/2.5/onecall?lon=74.59&lat=42.87&exclude=hourly,minutely,current,alerts&appid=a9625fde9a815d299c2e9a3e73429e71

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start', 'старт'])
def welcome(message):
	bot.send_message(message.chat.id, 'Добро пожаловать, ' + str(message.from_user.username))



@bot.message_handler(content_types=['text'])
def weather_send(message):
	city = message.text
	url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={config.api_key}&units=metric'
	
	try:
		
		result = requests.get(url)
		weather = result.json()

		bot.send_message(message.chat.id, 'В городе '
						+ str(weather['name']) + ' температура: '
		 				+ str(float(weather['main']['temp'])) + ' °C' + '\n'
		 				+ 'Максимальная температура: '
		 				+ str(float(weather['main']['temp_max'])) + ' °C' + '\n'
		 				+ 'Минимальная температура: '
		 				+ str(float(weather['main']['temp_min'])) + ' °C' + '\n'
		 				+ 'Давление: '
		 				+ str(float(weather['main']['pressure'])) + '\n'
		 				+ 'Влажность: '
		 				+ str(float(weather['main']['humidity'])) + '\n')


	except:
		bot.send_message(message.chat.id, 'Город ' + city + ' не найден!')





if __name__ == '__main__':
	bot.polling(none_stop=True, interval=0)
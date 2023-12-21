import telebot

import requests

# красивый вывод информации
from telebot import types
import html2text

from config import TOKEN

# получение информации об обьектах
objects_lst = 'https://klevoemestechko.ru/catalog/api/spots/'
response_objects = requests.get(objects_lst)
response_objects = response_objects.json()
# создание списка с обьектами
places = [el['name'] for el in response_objects]

districts_lst = 'https://klevoemestechko.ru/catalog/api/regions/'
response_districts = requests.get(districts_lst)
response_districts = response_districts.json()
districts = [el['region'] for el in response_districts]

bot = telebot.TeleBot(TOKEN)

# раговорные фразы
yes = ['да', 'конечно', 'да.', 'Да', 'Да.', 'Конечно', 'Ещё бы', '1', 'yes', 'Yes']
no = ['нет', 'Нет', 'не', 'Не', 'Неа', '0', 'No', 'no']
hi = ['Привет', 'Где отдохнуть?', ' Подскажи, куда прокатиться на выходные?',
      'Куда поехать', 'Куда поехать?', 'Куда поехать на рыбалку?']
do = ['Как дела?', 'как дела?', 'Как дела', 'как дела']
all_pl = ['Все места для рыбалки', 'Все', 'все места для рыбалки', 'все']
dist_lst = []


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    yes_button = types.KeyboardButton('Да')
    no_button = types.KeyboardButton('Нет')
    markup.add(yes_button)
    markup.add(no_button)
    bot.send_message(message.chat.id, f'Привет! \u270B Хочешь отправиться на рыбалку?',
                     parse_mode='Markdown', reply_markup=markup)


@bot.message_handler(commands=['help'])
def help(message):
    # создание кнопок
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    dist_button = types.KeyboardButton('По регионам')
    all_button = types.KeyboardButton('Все места для рыбалки')
    markup.add(dist_button)
    markup.add(all_button)

    # отправка сообщения
    bot.send_message(message.chat.id, 'Привет! Я подскажу где порыбачить',
                     parse_mode='Markdown', reply_markup=markup)


@bot.message_handler()
def get_user_text(message):
    # если пользователь хочет выбрать район
    if message.text == 'По регионам':
        # создание кнопок
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        back = types.KeyboardButton('Назад')
        markup.add(back)
        for el in districts:
            button = types.KeyboardButton(el)
            markup.add(button)

        # отправка сообщения
        bot.send_message(message.chat.id, 'Выберите регион', reply_markup=markup)
        return

    # если пользователь приветствует бота
    elif message.text in hi:
        msg = bot.send_message(message.chat.id, f'Привет! \u270B Хочешь отправиться на рыбалку?',
                               parse_mode='Markdown')

        # отправка сообщения
        # следующая по очереди фунция 'yes_or_not'
        bot.register_next_step_handler(msg, yes_or_not)

    # если пользователь выбрал район
    elif message.text in districts:
        # # создание кнопок
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        back = types.KeyboardButton('Назад')
        markup.add(back)
        for el in response_objects:
            for i in response_districts:
                if i['id'] == el['region']:
                    if i['region'] == message.text:
                        button = types.KeyboardButton(el['name'])
                        markup.add(button)

        # отправка сообщения
        bot.send_message(message.chat.id, 'Выберите место для рыбалки', reply_markup=markup)
        return

    # если пользователь выбрал место
    elif message.text in places:
        for el in response_objects:
            if el['name'] == message.text:
                # название места
                name = el['name']

                # id места
                id_object = el['id']

                # описание места
                description = el['text']
                description = html2text.html2text(description)

                # фото места
                image = el['img']

                # координаты места
                cords = f"{el['lat']} {el['lon']}"

                for i in response_districts:
                    if i['id'] == el['region']:
                        district = i['region']

        dist_lst.append(district)

        # создание кнопок
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

        # отправка фото места
        bot.send_photo(message.chat.id, image)

        # если сообщение слишком длинное
        if len(description) < 4096:
            # отправка сообщения
            bot.send_message(message.chat.id, f'*{name}*\n\n'
                                              f'[{cords}](https://yandex.ru/maps/36/stavropol/?ll={cords.split()[1]}%2'
                                              f'C{cords.split()[0]}&mode=whatshere&whatshere%5Bpoint%5D={cords.split()[1]}%'
                                              f'2C{cords.split()[0]}&whatshere%5Bzoom%5D=16&z=15)\n\n'
                                              f'{district}\n\n'
                                              f'{description}', parse_mode='Markdown', reply_markup=markup)
        else:
            for x in range(0, len(description), 4096):
                # отправка сообщения
                bot.send_message(message.chat.id, description[x:x + 4096])
        return

    # если пользователь хочет вернуться назад
    elif message.text == 'Назад':
        # возвращение на начальную страницу
        start(message)

    # если пользователь хочет просмотреть все места
    elif message.text == 'Все места для рыбалки':
        # создание кнопок
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        back = types.KeyboardButton('Назад')
        markup.add(back)
        for el in places:
            button = types.KeyboardButton(el)
            markup.add(button)
        more = types.KeyboardButton('Далее')
        markup.add(more)

        # отправка сообщения
        bot.send_message(message.chat.id, 'Выберите место для рыбалки', reply_markup=markup)

    # если пользователь отвечает да
    elif message.text in yes:
        msg = bot.send_message(message.chat.id, f'Хочешь классно порыбачить?',
                               parse_mode='Markdown')

        # отправка сообщения
        # следующая по очереди фунция 'yes_or_not'
        bot.register_next_step_handler(msg, yes_or_not)

    # если пользователь хочет узнать куда поехать
    elif message.text in do:
        msg = bot.send_message(message.chat.id, f'Хочешь классно порыбачить?',
                               parse_mode='Markdown')

        # отправка сообщения
        # следующая по очереди фунция 'yes_or_not'
        bot.register_next_step_handler(msg, yes_or_not)


# ответ на 'да' или 'нет'
def yes_or_not(message):
    # если пользователь отвечает да
    if message.text in yes:
        msg = bot.send_message(message.chat.id, f'Вот список регионов с классными местами для рыбалки. Выбирай.',
                               parse_mode='Markdown')
        # создание кнопок
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        back = types.KeyboardButton('Назад')
        markup.add(back)
        for el in districts:
            button = types.KeyboardButton(el)
            markup.add(button)
        bot.send_message(message.chat.id, 'Выберите регион', reply_markup=markup)

        # отправка сообщения
        # следующая по очереди фунция 'get_user_text'
        bot.register_next_step_handler(msg, get_user_text)

    # если пользователь приветсвует бота
    elif message.text in hi:
        msg = bot.send_message(message.chat.id, f'Хочешь классно порыбачить?',
                               parse_mode='Markdown')

        # отправка сообщения
        # следующая по очереди фунция 'yes_or_not'
        bot.register_next_step_handler(msg, yes_or_not)

    # если пользователь отвечает нет
    elif message.text in no:
        msg = bot.send_message(message.chat.id, f'Тогда я отдохну. \U0001F634', parse_mode='Markdown')

        # отправка сообщения
        # следующая по очереди фунция 'get_user_text'
        bot.register_next_step_handler(msg, get_user_text)

    # если пользователь хочет узнать куда поехать
    elif message.text in do:
        msg = bot.send_message(message.chat.id, f'Хочешь классно порыбачить?',
                               parse_mode='Markdown')

        # отправка сообщения
        # следующая по очереди фунция 'get_user_text'
        bot.register_next_step_handler(msg, get_user_text)

    # если пользователь бот не понял пользователя
    else:
        msg = bot.send_message(message.chat.id, f'Я вас не понимаю.', parse_mode='Markdown')

        # отправка сообщения
        # следующая по очереди фунция 'get_user_text'
        bot.register_next_step_handler(msg, get_user_text)


bot.polling(none_stop=True)

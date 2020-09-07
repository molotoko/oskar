import random
import telebot
import schedule
import requests
import lxml.html as html
import unicodedata
import time
from datetime import datetime

from common.config import telegram_api_key
from common.vars import kinochat_id, members_list, stickers_list, genre_list
from common.helpers import random_member, get_random_actor

bot = telebot.TeleBot(telegram_api_key)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Приветствую тебя, о киноман!')


@bot.message_handler(commands=['help'])
def help_me(message):
    bot.send_message(
        message.chat.id,
        f'Добро пожаловать к Оскару в Киноклуб! Не считая меня, в клубе уже *{len(members_list)}* участников! '
        f'Ниже представлен список моих услуг. '
        f'Помните: судьба может сыграть с вами злую шутку!\n'
        f'/member расскажет обо всех ваших кинотайнах;\n'
        f'/film выберет за вас случайное кино;\n'
        f'/genre поможет выбрать жанр для голосований (если повезет — с эротикой);\n'
        f'/vip определит особо голосистого участника этого голосования: '
        f'может отдать 4 голоса вместо 2, максимум 2 за 1 фильм;\n'
        f'/kinoman даст одному из вас возможность сразу предложить фильм вне очереди.\n'
        f'/droed пнуть робота.\n'
        f'/date сходить на свидание с оскароносцем!\n'
        f'/born узнать, кто из знаменитостей родился сегодня.\n',
        parse_mode='Markdown'
    )


@bot.message_handler(commands=['member'])
def member_info(message):
    get_info = 'собрать инфу из таблички'
    find_member_info = 'вытащить инфу о конкретном члене клуба'
    bot.send_message(
        message.chat.id,
        f'Ваша статистика пока недоступна. И будет недоступна еще какое-то время. Заполняйте табличку!'
    )


@bot.message_handler(commands=['film'])
def random_film(message):
    page = requests.get('https://www.kinopoisk.ru/afisha/new/city/1/')
    tree = html.fromstring(page.text)
    film_name = tree.xpath('//div[@class="randomMovie"]//a/span/u/text()')[0]
    film_name_normalized = unicodedata.normalize("NFKD", film_name)
    film_path = 'film/301/'

    all_links = list(tree.iterlinks())
    for link in all_links:
        (element, attribute, url, pos) = link
        if 'level/1/film' in url:
            film_path = url[8:]
    film_link = f'https://www.kinopoisk.ru{film_path}'

    bot.send_message(
        message.chat.id,
        f'Вам придется посмотреть фильм "{film_name_normalized}": {film_link}',
        reply_to_message_id=message.message_id
    )


@bot.message_handler(commands=['genre'])
def random_genre(message):
    genre_value = random.choice(genre_list)

    erotic = ' с эротикой'
    if random.randrange(0, 100) < 2:
        genre_value = f'{genre_value}{erotic}'

    bot.send_message(
        message.chat.id,
        f'*Выбран жанр*: {genre_value}.',
        parse_mode='Markdown',
        reply_to_message_id=message.message_id
    )


@bot.message_handler(commands=['vip'])
def get_vip(message):
    bot.send_message(
        message.chat.id,
        f'Киноман *{random_member()}* получил статус *VIP*. Это значит, что он имеет 4 голоса вместо 2 и может '
        f'распределить их как угодно, но не более 2 голосов за 1 фильм.',
        parse_mode='Markdown'
    )


@bot.message_handler(commands=['kinoman'])
def kinoman_of_the_week(message):
    bot.send_message(
        message.chat.id,
        f'Киноман *{random_member()}* становится почетным *Киноманом Недели*. '
        f'Он может предложить любой фильм к просмотру вне очереди!',
        parse_mode='Markdown'
    )


@bot.message_handler(commands=['santa'])
def santa(message):
    bot.send_message(
        message.chat.id,
        f'Киноман *{random_member()}* становится Сантой. '
        f'Он может предложить любой фильм к просмотру вне очереди!\n'
        f'Этот фильм мы занесем в Коллективные просмотры!',
        parse_mode='Markdown'
    )


@bot.message_handler(commands=['droed'])
def go_to_work(message):
    bot.send_sticker(message.chat.id, stickers_list['droed'])
    bot.send_sticker(message.chat.id, stickers_list['droed_work'])


@bot.message_handler(commands=['date'])
def random_actor(message):
    username = f'@{message.from_user.username}'

    member_gender = None
    for member in members_list:
        if member['username'] == username:
            member_gender = member['gender']
            break

    request_gender = None
    if member_gender == 'male':
        request_gender = 'female'
    elif member_gender == 'female':
        request_gender = 'male'

    actor = None
    while actor == None:
        random_actor = get_random_actor(request_gender)
        if random_actor['alive']:
            actor = random_actor

    actor_name = actor['name']
    actor_link = actor['link']

    bot.reply_to(
        message,
        f'Ты идешь на свидание с *{actor_name}*!\n'
        f'{actor_link}',
        parse_mode='Markdown'
    )


@bot.message_handler(commands=['born'])
def born_today(message):
    request_link = 'https://www.imdb.com/feature/bornondate/'
    page = requests.get(request_link)
    tree = html.fromstring(page.text)

    born_list = []
    celebrities = tree.find_class('lister-item')[:5]

    for celebrity in celebrities:
        celebrity_anchor = celebrity.find_class('lister-item-header')[0].find('a')
        celebrity_name = celebrity_anchor.text_content().strip()
        celebrity_link = celebrity_anchor.attrib['href']
        born_list.append([celebrity_name, celebrity_link])

    born_message = f'Сегодня родились знаменитости:\n'
    for celebrity in born_list:
        born_message += f'[{celebrity[0]}](https://www.imdb.com{celebrity[1]})\n'

    bot.send_message(
        message.chat.id,
        born_message,
        parse_mode='Markdown'
    )


def born_today_results():
    request_link = 'https://www.imdb.com/feature/bornondate/'
    page = requests.get(request_link)
    tree = html.fromstring(page.text)

    born_list = []
    celebrities = tree.find_class('lister-item')[:5]

    for celebrity in celebrities:
        celebrity_anchor = celebrity.find_class('lister-item-header')[0].find('a')
        celebrity_name = celebrity_anchor.text_content().strip()
        celebrity_link = celebrity_anchor.attrib['href']
        born_list.append([celebrity_name, celebrity_link])

    born_message = f'Сегодня родились знаменитости:\n'
    for celebrity in born_list:
        born_message += f'[{celebrity[0]}](https://www.imdb.com{celebrity[1]})\n'

    bot.send_message(
        kinochat_id,
        born_message,
        parse_mode='Markdown'
    )


@bot.message_handler(func=lambda message: False)
def scheduled_events():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    if current_time == '18:16:00':
        born_today_results()


@bot.message_handler(content_types=['text'])
def send_text(message):
    hello_list = ['привет', 'hello', 'hi', 'приветствую', 'здравствуй', 'здравствуйте', 'хелло', 'хэлло', 'йоу',
                  'здрасьте', 'дратути', 'драсьте']
    if message.text.lower() in hello_list:
        bot.send_message(message.chat.id, 'Привет, киноман!', reply_to_message_id=message.message_id)
    elif message.text.lower() == 'пока':
        bot.send_message(message.chat.id, 'I\'ll be back!', reply_to_message_id=message.message_id)
    elif 'дроед' in message.text.lower():
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAOvXrszrgvwIgKSJj105YntGMYTL7cAAl4BAAJEyQkHQhFYn9ziwn4ZBA')
    elif 'дроид' in message.text.lower():
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAOvXrszrgvwIgKSJj105YntGMYTL7cAAl4BAAJEyQkHQhFYn9ziwn4ZBA')


# @bot.message_handler(content_types=['sticker'])
# def send_sticker_id(message):
#     bot.send_message(message.chat.id, message.sticker.file_id)


bot.polling()
notifications()

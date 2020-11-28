import random
import telebot
import schedule
import requests
import lxml.html as html
import unicodedata
import time
from threading import Thread

from common.config import telegram_api_key
from common.vars import kinochat_id, members_list, help_msg, stickers_list, genre_list
from common.helpers import random_member, get_random_actor, get_random_director, born_today

bot = telebot.TeleBot(telegram_api_key)


@bot.message_handler(commands=['start', 'help'])
def help_me(message):
    bot.send_message(message.chat.id, help_msg, parse_mode='Markdown')


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

    request_gender = 'female' if member_gender == 'male' else 'male'

    actor = None
    while not actor:
        random_actor = get_random_actor(request_gender)
        if random_actor['alive']:
            actor = random_actor

    actor_name = actor['name']
    actor_link = actor['link']

    bot.send_message(
        message.chat.id,
        f'Ты идешь на свидание с *{actor_name}*!\n{actor_link}',
        parse_mode='Markdown',
        reply_to_message_id=message.message_id
    )


@bot.message_handler(commands=['director'])
def random_director(message):
    director = get_random_director()
    director_name = director['name']
    director_link = director['link']

    bot.send_message(
        message.chat.id,
        f'Обсуждаем режиссера *{director_name}*!\n{director_link}',
        parse_mode='Markdown'
    )


def born_today_results():
    born_message = born_today()

    return bot.send_message(
        kinochat_id,
        born_message,
        parse_mode='Markdown'
    )


def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(1)


@bot.message_handler(content_types=['text'])
def send_text(message):
    hello_list = ['привет', 'hello', 'hi', 'приветствую', 'здравствуй', 'здравствуйте', 'хелло', 'хэлло', 'йоу',
                  'здрасьте', 'дратути', 'драсьте']
    if message.text.lower() in hello_list:
        bot.send_message(message.chat.id, 'Привет, киноман!', reply_to_message_id=message.message_id)
    elif message.text.lower() == 'пока':
        bot.send_message(message.chat.id, 'I\'ll be back!', reply_to_message_id=message.message_id)
    # elif 'дроед' in message.text.lower():
    #     bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAOvXrszrgvwIgKSJj105YntGMYTL7cAAl4BAAJEyQkHQhFYn9ziwn4ZBA')
    # elif 'дроид' in message.text.lower():
    #     bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAOvXrszrgvwIgKSJj105YntGMYTL7cAAl4BAAJEyQkHQhFYn9ziwn4ZBA')


if __name__ == "__main__":
    # scheduled messages here
    schedule.every().day.at('11:30').do(born_today_results)
    Thread(target=schedule_checker).start()

    # start the bot
    bot.polling()
